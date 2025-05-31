import pytest
from django.urls import reverse
from ads.models import Ad, Exchange


@pytest.mark.django_db
def test_my_offers_view(
    client,
    user_one_logged_in,
    exchange_one,
    exchange_two,
):
    """Проверка корректное на отображение предложений пользователя."""

    url = reverse("ads:my_offers")
    response = client.get(url)

    assert response.status_code == 200
    assert exchange_one in response.context["offers"]
    assert exchange_two not in response.context["offers"]


@pytest.mark.django_db
def test_ads_incoming_view(
    client,
    user_one_logged_in,
    exchange_one,
    exchange_two,
):
    """Проверка корректное на отображение предложений пользователя."""
    client.login(username="user_one", password="2121")
    url = reverse("ads:incoming_requests")
    response = client.get(url)

    assert response.status_code == 200
    assert "Мои предложения" in response.content.decode()
    assert exchange_one not in response.context["exchanges"]
    assert exchange_two in response.context["exchanges"]


@pytest.mark.django_db
def test_accept_exchange_view(
    client,
    user_two_logged_in,
    exchange_one,
):
    """Проверка изменения статуса при принятии предложения."""

    assert exchange_one.status.status == "Ожидание"
    url = reverse(
        "ads:exchange_accept",
        kwargs={"pk": exchange_one.pk},
    )
    response = client.get(url)
    exchange_one.refresh_from_db()
    assert exchange_one.status.status == "Принято"
    assert response.status_code == 302
    assert response.url == reverse("ads:incoming_requests")


@pytest.mark.django_db
def test_accept_exchange_wrong_user(
    client,
    user_one_logged_in,
    exchange_one,
):
    """Проверка изменения статуса при
    принятии предложения не тем пользователем."""

    url = reverse(
        "ads:exchange_accept",
        kwargs={"pk": exchange_one.pk},
    )
    response = client.get(url)
    assert response.status_code == 404
    exchange_one.refresh_from_db()
    assert exchange_one.status.status == "Ожидание"


@pytest.mark.django_db
def test_reject_exchange_view(
    client,
    user_two_logged_in,
    exchange_one,
):
    """Проверка изменения статуса при отклонении предложения."""

    assert exchange_one.status.status == "Ожидание"
    url = reverse(
        "ads:exchange_reject",
        kwargs={"pk": exchange_one.pk},
    )
    response = client.get(url)
    exchange_one.refresh_from_db()
    assert exchange_one.status.status == "Отклонено"
    assert response.status_code == 302
    assert response.url == reverse("ads:incoming_requests")


@pytest.mark.django_db
def test_reject_exchange_wrong_user(
    client,
    user_one_logged_in,
    exchange_one,
):
    """Проверка изменения статуса при
    отклонении предложения не тем пользователем."""

    url = reverse(
        "ads:exchange_reject",
        kwargs={"pk": exchange_one.pk},
    )
    response = client.get(url)
    assert response.status_code == 404
    exchange_one.refresh_from_db()
    assert exchange_one.status.status == "Ожидание"


@pytest.mark.django_db
def test_delete_exchange(
    client,
    user_one_logged_in,
    exchange_one,
):
    url = reverse(
        "ads:exchange_delete",
        kwargs={"pk": exchange_one.pk},
    )
    response = client.post(url)
    assert response.status_code == 302
    exchanges = Exchange.objects.all()
    assert exchange_one not in exchanges


@pytest.mark.django_db
def test_delete_exchange_wrong_user(
    client,
    user_two_logged_in,
    exchange_one,
):
    url = reverse(
        "ads:exchange_delete",
        kwargs={"pk": exchange_one.pk},
    )
    response = client.post(url)
    assert response.status_code == 404
    exchanges = Exchange.objects.all()
    assert exchange_one in exchanges


@pytest.mark.django_db
def test_index(client):
    url = reverse("ads:index")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ads_list_view(client, ad_one, ad_two, ad_tree):
    """Тест на корректное отображение"""
    url = reverse("ads:list")
    response = client.get(url)
    assert response.status_code == 200
    assert "object_list" in response.context
    assert ad_one in response.context["object_list"]
    assert ad_two in response.context["object_list"]
    assert ad_tree in response.context["object_list"]


@pytest.mark.django_db
def test_ads_list_view_search(
    client,
    ad_one,
    ad_two,
):
    """Тест поиска"""
    url = reverse("ads:list")
    response = client.get(
        url,
        {"search": "car"},
    )
    assert response.status_code == 200
    object_list = response.context["object_list"]
    assert ad_one in object_list
    assert ad_two not in object_list


@pytest.mark.django_db
def test_ads_list_view_filter_by_category(
    client,
    ad_one,
    ad_two,
    category_car,
):
    """Тест фильтра по категориям"""
    url = reverse("ads:list")
    response = client.get(
        url,
        {"category": str(category_car.pk)},
    )
    assert response.status_code == 200
    object_list = response.context["object_list"]
    assert all(ad.category == category_car for ad in object_list)


@pytest.mark.django_db
def test_ads_list_view_filter_by_condition(
    client,
    ad_two,
    ad_tree,
    condition_new,
):
    """Тест фильтра по состоянию"""
    url = reverse("ads:list")
    response = client.get(
        url,
        {"condition": str(condition_new.pk)},
    )
    assert response.status_code == 200
    object_list = response.context["object_list"]
    assert ad_tree in object_list
    assert ad_two not in object_list


@pytest.mark.django_db
def test_ads_list_view_serch_filters(
    client,
    ad_one,
    condition_new,
    category_car,
):
    """Тест на поиск и фильтр"""
    url = reverse("ads:list")
    response = client.get(
        url,
        {
            "search": "car",
            "category": str(category_car.pk),
            "condition": str(condition_new.pk),
        },
    )
    assert response.status_code == 200
    object_list = response.context["object_list"]
    assert ad_one in object_list
    assert all(
        ad.category == category_car and ad.condition == condition_new
        for ad in object_list
    )


@pytest.mark.django_db
def test_ads_list_view_context_fields(client):
    url = reverse("ads:list")
    response = client.get(url)
    context = response.context
    assert "categories" in context
    assert "conditions" in context
    assert "current_search" in context
    assert "current_category" in context
    assert "current_condition" in context


@pytest.mark.django_db
def test_ad_detail(client, ad_two):
    """Тест на получение информации по объявлению."""
    url = reverse(
        "ads:detail",
        kwargs={"pk": ad_two.pk},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert "object" in response.context
    assert response.context["object"] == ad_two


@pytest.mark.django_db
def test_ad_delete(
    client,
    user_two_logged_in,
    ad_two,
):
    """Тест на удаление владельцу."""
    url = reverse(
        "ads:delete",
        kwargs={"pk": ad_two.pk},
    )
    response = client.post(url)
    ads = Ad.objects.all()
    assert response.status_code == 302
    assert response.url == reverse("ads:list")
    assert ad_two not in ads


@pytest.mark.django_db
def test_ad_delete_no_auth_user(
    client,
    ad_two,
):
    """Тест на удаление не зарегистрированному пользователю
    которого редериктет на страницу login.html."""
    url = reverse(
        "ads:delete",
        kwargs={"pk": ad_two.pk},
    )
    response = client.post(url)
    ads = Ad.objects.all()
    assert response.url == reverse("ads:login")
    assert response.status_code == 302
    assert ad_two in ads


@pytest.mark.django_db
def test_ad_delete_wrong_user(
    client,
    user_one_logged_in,
    ad_two,
):
    """Тест на удаление зарегистрированному, но не владельцу, пользователю."""
    url = reverse(
        "ads:delete",
        kwargs={"pk": ad_two.pk},
    )
    response = client.post(url)
    ads = Ad.objects.all()
    assert response.status_code == 403
    assert ad_two in ads


@pytest.mark.django_db
def test_ad_edit(
    client,
    user_two_logged_in,
    category_car,
    condition_old,
    ad_two,
):
    """Тест на редактирование владельцем."""
    url = reverse(
        "ads:edit",
        kwargs={"pk": ad_two.pk},
    )
    response = client.post(
        url,
        {
            "title": "title test",
            "description": "description test",
            "category": category_car.id,
            "condition": condition_old.id,
            "image_url": ad_two.image_url,
        },
    )
    assert response.status_code == 302
    ad_two.refresh_from_db()
    assert ad_two.title == "title test"
    assert ad_two.category.name == "Cars"
    assert ad_two.condition.name == "Б/У"
    assert ad_two.description == "description test"


@pytest.mark.django_db
def test_ad_edit_wrong_user(
    client,
    user_one_logged_in,
    category_car,
    condition_old,
    ad_two,
):
    """Тест на редактирование не владельцем."""
    url = reverse(
        "ads:edit",
        kwargs={"pk": ad_two.pk},
    )
    response = client.post(
        url,
        {
            "title": "title test",
            "description": "description test",
            "category": category_car.id,
            "condition": condition_old.id,
            "image_url": ad_two.image_url,
        },
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_ad_create_authenticated_user(
    client,
    user_one_logged_in,
    category_books,
    condition_new,
):
    """Создание объявления авторизованным пользователем."""
    url = reverse("ads:create")
    response = client.post(
        url,
        {
            "title": "Test Ad",
            "description": "Test description",
            "image_url": "https://img.freepik.com/premium-vector/no-photo-available-vector-icon-default-image-symbol-picture-coming-soon-web-site-mobile-app_87543-18055.jpg",
            "category": category_books.id,
            "condition": condition_new.id,
        },
    )

    assert response.status_code == 302
    ad = Ad.objects.get(title="Test Ad")
    assert ad.description == "Test description"
    assert ad.user == user_one_logged_in


@pytest.mark.django_db
def test_ad_create_unauthenticated_user(
    client,
    category_books,
    condition_new,
):
    """Создание объявления неавторизованным пользователем."""
    url = reverse("ads:create")
    response = client.post(
        url,
        {
            "title": "Test Ad",
            "description": "Test description",
            "category": category_books.id,
            "condition": condition_new.id,
            "image_url": "https://img.freepik.com/premium-vector/no-photo-available-vector-icon-default-image-symbol-picture-coming-soon-web-site-mobile-app_87543-18055.jpg",
        },
    )

    assert response.status_code == 302
    assert response.url.startswith(str(reverse("ads:login")))


@pytest.mark.django_db
def test_ad_create_invalid_form(client, user_one_logged_in):
    """Попытка отправки невалидной формы (без обязательных полей)."""
    url = reverse("ads:create")
    response = client.post(
        url,
        {
            "title": "",
        },
    )
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors
    assert Ad.objects.count() == 0


@pytest.mark.django_db
def test_create_exchange_success(
    client,
    user_one_logged_in,
    ad_one,
    ad_two,
):
    """Пользователь отправляет запрос на обмен."""

    url = reverse(
        "ads:create_exchange",
        kwargs={"pk": ad_two.pk},
    )

    response = client.post(
        url,
        {
            "ad_sender": ad_one.pk,
            "ad_receiver": ad_two.pk,
            "comment": "test comment",
        },
    )

    assert response.status_code == 302
    assert Exchange.objects.count() == 1
    exchange = Exchange.objects.first()
    assert exchange.ad_sender == ad_one
    assert exchange.ad_receiver == ad_two
    assert exchange.status.status == "Ожидание"


@pytest.mark.django_db
def test_create_exchange_to_own_ad_forbidden(
    client,
    user_one_logged_in,
    ad_one,
):
    url = reverse("ads:create_exchange", kwargs={"pk": ad_one.pk})
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_exchange_same_ad(
    client,
    user_two_logged_in,
    ad_two,
):
    url = reverse(
        "ads:create_exchange",
        kwargs={"pk": ad_two.pk},
    )
    response = client.post(url, {"ad_sender": ad_two.pk})
    assert response.status_code == 403
    assert Exchange.objects.count() == 0


@pytest.mark.django_db
def test_exchange_duplicate_filtered_out(
    client,
    user_one_logged_in,
    ad_one,
    ad_two,
    exchange_one,
):
    """
    Повторный обмен с уже использованным ad_sender/ad_receiver невозможен.
    """
    url = reverse("ads:create_exchange", kwargs={"pk": ad_two.pk})
    response = client.get(url)
    form = response.context["form"]
    assert ad_one not in form.fields["ad_sender"].queryset


@pytest.mark.django_db
def test_create_exchange_redirect_for_anonymous(client, ad_two):
    url = reverse("ads:create_exchange", kwargs={"pk": ad_two.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "/login/" in response.url
