import pytest
from ads.serializers import (
    CategorySerializer,
    ConditionSerializer,
    AdSerializer,
    ExchangeStatusSerializer,
    ExchangeSerializer,
)
from ads.models import Ad

def test_category_serializer(category_books):
    """
    Проверяет сериализацию категории
    """
    serializer = CategorySerializer(category_books)
    assert serializer.data["id"] == category_books.id
    assert serializer.data["name"] == category_books.name


def test_condition_serializer(condition_new):
    """
    Проверяет сериализацию состояния
    """
    serializer = ConditionSerializer(condition_new)
    assert serializer.data["id"] == condition_new.id
    assert serializer.data["name"] == condition_new.name


def test_ad_serializer(ad_one):
    """
    Проверяет сериализацию объявления
    """
    serializer = AdSerializer(ad_one)
    assert serializer.data["id"] == ad_one.id
    assert serializer.data["title"] == ad_one.title
    assert serializer.data["user"] == str(ad_one.user)
    assert serializer.data["description"] == ad_one.description


def test_exchange_status_serializer(exchange_status_waiting):
    """
    Проверяет сериализацию статуса обмена
    """
    serializer = ExchangeStatusSerializer(exchange_status_waiting)
    assert serializer.data["id"] == exchange_status_waiting.id
    assert serializer.data["status"] == exchange_status_waiting.status


@pytest.mark.django_db
def test_exchange_serializer_valid(
    ad_one,
    ad_two,
):
    """
    Проверяет корректную валидацию и сохранение обмена
    """
    data = {
        "ad_sender_id": ad_one.id,
        "ad_receiver_id": ad_two.id,
        "comment": "test",
    }
    serializer = ExchangeSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    validated = serializer.validated_data
    assert validated["ad_sender"] == ad_one
    assert validated["ad_receiver"] == ad_two
    assert validated["comment"] == "test"
    assert validated["status"].status == "Ожидание"
    exchange = serializer.save()
    assert exchange.ad_sender == ad_one
    assert exchange.ad_receiver == ad_two
    assert exchange.comment == "test"
    assert exchange.status.status == "Ожидание"


@pytest.mark.django_db
def test_exchange_serializer_invalid_same_ad(ad_one):
    """
    Проверяет ошибку при попытке обмена одного и того же объявления
    """
    data = {
        "ad_sender_id": ad_one.id,
        "ad_receiver_id": ad_one.id,
        "comment": "Тестируем ошибку",
    }
    serializer = ExchangeSerializer(data=data)
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors
    assert (
        "Нельзя обменивать одно и то же объявление."
        in serializer.errors["non_field_errors"]
    )


@pytest.mark.django_db
def test_exchange_serializer_invalid_same_user(
    ad_one,
    ad_four,
):
    """
    Проверяет ошибку при попытке обмена объявлениями одного пользователя
    """
    data = {
        "ad_sender_id": ad_one.id,
        "ad_receiver_id": ad_four.id,
        "comment": "Тестируем ошибку",
    }
    serializer = ExchangeSerializer(data=data)
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors
    assert (
        "Нельзя обмениваться объявлениями одного пользователя."
        in serializer.errors["non_field_errors"]
    )


@pytest.mark.django_db
def test_ad_serializer_create(
    user_one,
    category_books,
    condition_new,
):
    """
    Проверяет создание нового объявления через сериализатор
    """
    data = {
        "title": "New Ad",
        "description": "Описание объявления",
        "image_url": "https://example.com/image.jpg",
        "category": category_books.id,
        "condition": condition_new.id,
    }

    serializer = AdSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    ad = serializer.save(user=user_one)

    assert ad.title == data["title"]
    assert ad.description == data["description"]
    assert ad.image_url == data["image_url"]
    assert ad.category == category_books
    assert ad.condition == condition_new
    assert ad.user == user_one


@pytest.mark.django_db
def test_ad_serializer_update(
    ad_one,
    category_books,
    condition_old,
):
    """
    Проверяет обновление существующего объявления через сериализатор
    """
    data = {
        "title": "Updated Car",
        "description": "Updated black car",
        "image_url": "https://example.com/car.jpg",
        "category": category_books.id,
        "condition": condition_old.id,
    }

    serializer = AdSerializer(
        instance=ad_one,
        data=data,
    )
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()

    assert updated.title == "Updated Car"
    assert updated.description == "Updated black car"
    assert updated.image_url == "https://example.com/car.jpg"
    assert updated.category == category_books
    assert updated.condition == condition_old


@pytest.mark.django_db
def test_ad_delete(ad_four):
    """
    Проверяет удаление объявления
    """
    ad_id = ad_four.id
    ad_four.delete()
    assert not Ad.objects.filter(id=ad_id).exists()
