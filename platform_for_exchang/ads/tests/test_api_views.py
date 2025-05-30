import pytest
from rest_framework.test import APIClient
from ads.models import Exchange, ExchangeStatus
from ads.serializers import AdSerializer, ExchangeSerializer

client = APIClient()


@pytest.mark.django_db
def test_login_check():
    """
    Проверяет, что неавторизованный пользователь может просматривать объявления
    """
    response = client.get("/api/ads/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_ad(
    user_one_logged,
    category_books,
    condition_new,
):
    """
    Проверяет, что авторизованный пользователь может создать объявление
    """
    client, _ = user_one_logged
    data = {
        "title": "New Book",
        "description": "A nice read",
        "image_url": "",
        "category": category_books.id,
        "condition": condition_new.id,
    }
    response = client.post(
        "/api/ads/",
        data,
    )
    assert response.status_code == 201
    assert response.data["title"] == "New Book"


@pytest.mark.django_db
def test_create_ad_unauthenticated(
    category_books,
    condition_new,
):
    """
    Проверяет, что неавторизованный пользователь не может создать объявление
    """
    data = {
        "title": "Unauthorized Ad",
        "description": "Should not be allowed",
        "image_url": "",
        "category": category_books.id,
        "condition": condition_new.id,
    }
    client.logout()
    response = client.post(
        "/api/ads/",
        data,
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_edit_own_ad(
    user_one_logged,
    ad_one,
):
    """
    Проверяет, что пользователь может редактировать своё объявление
    """
    client, _ = user_one_logged
    data = {
        "title": "Updated Car",
        "description": ad_one.description,
        "category": ad_one.category.id,
        "condition": ad_one.condition.id,
    }
    response = client.put(
        f"/api/ads/{ad_one.id}/",
        data,
    )
    assert response.status_code == 200
    assert response.data["title"] == "Updated Car"


@pytest.mark.django_db
def test_edit_other_user_ad(
    user_two_logged,
    ad_one,
):
    """
    Проверяет, что пользователь не может редактировать чужое объявление
    """
    client, _ = user_two_logged
    data = {
        "title": "Hacked title",
        "description": ad_one.description,
        "category": ad_one.category.id,
        "condition": ad_one.condition.id,
    }
    response = client.put(
        f"/api/ads/{ad_one.id}/",
        data,
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_own_ad(
    user_one_logged,
    ad_four,
):
    """
    Проверяет, что пользователь может удалить своё объявление
    """
    client, _ = user_one_logged
    response = client.delete(f"/api/ads/{ad_four.id}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_other_user_ad(
    user_two_logged,
    ad_four,
):
    """
    Проверяет, что пользователь не может удалить чужое объявление
    """
    client, _ = user_two_logged
    response = client.delete(f"/api/ads/{ad_four.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_exchange(
    user_one_logged,
    ad_one,
    ad_two,
):
    """
    Проверяет, что владелец объявления может создать обмен
    """
    client, _ = user_one_logged
    data = {
        "ad_sender_id": ad_one.id,
        "ad_receiver_id": ad_two.id,
        "comment": "Let's trade",
    }
    response = client.post("/api/exchange/", data)
    assert response.status_code == 201
    assert response.data["comment"] == "Let's trade"
    assert response.data["ad_sender"]["id"] == ad_one.id


@pytest.mark.django_db
def test_create_exchange_not_owner(
    user_two_logged,
    ad_one,
    ad_two,
):
    """
    Проверяет, что нельзя создать обмен от чужого имени
    """
    client, _ = user_two_logged
    data = {
        "ad_sender_id": ad_one.id,
        "ad_receiver_id": ad_two.id,
        "comment": "I'm cheating",
    }
    response = client.post(
        "/api/exchange/",
        data,
    )
    assert response.status_code == 400
    assert "Вы можете создавать обмен только от своего имени" in str(
        response.data
    )


@pytest.mark.django_db
def test_accept_exchange(
    user_two_logged,
    exchange_one,
):
    """
    Проверяет, что получатель может принять обмен
    """
    client, _ = user_two_logged
    response = client.post(f"/api/exchange/{exchange_one.id}/accept_exchange/")
    assert response.status_code == 200
    exchange_one.refresh_from_db()
    assert exchange_one.status.status == "Принято"


@pytest.mark.django_db
def test_reject_exchange(
    user_two_logged,
    exchange_one,
):
    """
    Проверяет, что получатель может отклонить обмен
    """
    client, _ = user_two_logged
    response = client.post(f"/api/exchange/{exchange_one.id}/reject_exchange/")
    assert response.status_code == 200
    exchange_one.refresh_from_db()
    assert exchange_one.status.status == "Отклонено"


@pytest.mark.django_db
def test_accept_exchange_unauthorized(
    user_tree_logged,
    exchange_one,
):
    """
    Проверяет, что неучаствующий в обмене пользователь получает 404
    """
    client, _ = user_tree_logged
    response = client.post(f"/api/exchange/{exchange_one.id}/reject_exchange/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_reject_exchange(
    user_two_logged,
    exchange_one,
):
    """
    Проверяет, что получатель может отклонить обмен
    """
    client, _ = user_two_logged
    response = client.post(f"/api/exchange/{exchange_one.id}/reject_exchange/")
    assert response.status_code == 200
    exchange_one.refresh_from_db()
    assert exchange_one.status.status == "Отклонено"


@pytest.mark.django_db
def test_reject_exchange_not_receiver(
    user_tree_logged,
    exchange_one,
):
    """
    Проверяет, что не получатель не может отклонить обмен ожидается 404
    """
    client, _ = user_tree_logged
    response = client.post(f"/api/exchange/{exchange_one.id}/reject_exchange/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_filter_ads_by_category_and_condition(
    user_one_logged,
    ad_one,
    ad_four,
):
    """
    Проверяет фильтрацию объявлений по категории и состоянию
    """
    client, _ = user_one_logged

    response = client.get(
        "/api/ads/",
        {
            "category": ad_one.category.id,
            "condition": ad_one.condition.id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    titles = [ad["title"] for ad in data["results"]]
    assert "car" in titles
    assert "dog" in titles


@pytest.mark.django_db
def test_search_ads_by_title_and_description(
    user_one_logged,
    ad_one,
    ad_four,
):
    """
    Проверяет поиск по заголовку и описанию объявлений
    """
    client, _ = user_one_logged

    response = client.get(
        "/api/ads/",
        {"search": "car"},
    )
    assert response.status_code == 200
    data = response.json()
    assert any("car" in ad["title"].lower() for ad in data["results"])

    response = client.get(
        "/api/ads/",
        {"search": "white"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "dog"


@pytest.mark.django_db
def test_ads_pagination(
    user_one_logged,
    ad_one,
    ad_four,
):
    """
    Проверяет пагинацию объявлений
    """
    client, _ = user_one_logged

    response = client.get("/api/ads/?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    assert len(data["results"]) == 1
    assert data["count"] >= 2
