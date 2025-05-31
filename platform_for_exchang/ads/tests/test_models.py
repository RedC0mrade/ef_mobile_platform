from django.contrib.auth import get_user_model
from django.forms import ValidationError
import pytest

from ads.models import Ad, Category, Condition, Exchange

User = get_user_model()


def test_fixtures_users(
    user_one,
    user_two,
):
    users = User.objects.all()
    assert len(users) == 2
    assert user_one in users
    assert user_two in users


def test_fixtures_users_logged_in(
    user_one_logged_in,
    user_two_logged_in,
    user_tree_logged_in,
):
    assert user_one_logged_in, "Login failed"
    assert user_two_logged_in, "Login failed"
    assert user_tree_logged_in, "Login failed"


def test_fixtures_category(
    category_books,
    category_car,
):
    categories = Category.objects.all()
    assert len(categories) == 2
    assert category_books in categories
    assert category_car in categories


def test_fixtures_condition(
    condition_new,
    condition_old,
):
    conditions = Condition.objects.all()
    assert len(conditions) == 2
    assert condition_new in conditions
    assert condition_old in conditions


def test_fixtures_ad(
    ad_one,
    ad_two,
    ad_tree,
):
    ads = Ad.objects.all()
    assert len(ads) == 3
    assert ad_one in ads
    assert ad_two in ads
    assert ad_tree in ads


def test_fixtures_exchange(
    exchange_one,
    exchange_two,
):
    exchanges = Exchange.objects.all()
    assert len(exchanges) == 2
    assert exchange_one in exchanges
    assert exchange_two in exchanges


def test_create_exchange_for_self_ad(ad_one, exchange_status_waiting):
    """Проверяем создание обмена на одно и то же объявление"""

    with pytest.raises(ValidationError) as excinfo:
        Exchange.objects.create(
            ad_sender=ad_one,
            ad_receiver=ad_one,
            status=exchange_status_waiting,
        )
    error_message = excinfo.value.messages[0]
    assert "Нельзя обменивать одно и то же объявление." == error_message


def test_create_exchange_for_same_ad(
    ad_one,
    ad_four,
    exchange_status_waiting,
):
    """Проверяем создание обмена на свое объявление"""
    with pytest.raises(ValidationError) as excinfo:

        Exchange.objects.create(
            ad_sender=ad_one,
            ad_receiver=ad_four,
            status=exchange_status_waiting,
        )
    error_message = excinfo.value.messages[0]
    assert (
        "Нельзя обмениваться объявлениями одного пользователя." == error_message
    )


def test_cheak_unique_constraint(
    ad_one,
    ad_two,
    exchange_status_waiting,
):
    """Проверяем создание идентичного обмена"""
    with pytest.raises(ValidationError) as excinfo:
        Exchange.objects.create(
            ad_sender=ad_one,
            ad_receiver=ad_two,
            status=exchange_status_waiting,
        )

        Exchange.objects.create(
            ad_sender=ad_one,
            ad_receiver=ad_two,
            status=exchange_status_waiting,
        )

    error_message = excinfo.value.messages[0]
    assert (
        "Exchange with this Ad sender and Ad receiver already exists."
        == error_message
    )
