import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ads.models import Category, Condition, Ad, Exchange, ExchangeStatus


User = get_user_model()


@pytest.fixture
def user_one(db):
    return User.objects.create_user(
        username="user_one",
        password="2121",
    )


@pytest.fixture
def user_one_logged_in(
    client,
    user_one,
):
    client.login(
        username="user_one",
        password="2121",
    )
    return user_one


@pytest.fixture
def user_one_logged(user_one):
    client = APIClient()
    refresh = RefreshToken.for_user(user_one)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client, user_one


@pytest.fixture
def user_two(db):
    return User.objects.create_user(
        username="user_two",
        password="2121",
    )


@pytest.fixture
def user_two_logged_in(
    client,
    user_two,
):
    client.login(
        username="user_two",
        password="2121",
    )
    return user_two


@pytest.fixture
def user_two_logged(user_two):
    client = APIClient()
    refresh = RefreshToken.for_user(user_two)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client, user_two


@pytest.fixture
def user_tree(db):
    return User.objects.create_user(
        username="user_tree",
        password="2121",
    )


@pytest.fixture
def user_tree_logged_in(
    client,
    user_tree,
):
    client.login(
        username="user_tree",
        password="2121",
    )
    return user_tree


@pytest.fixture
def user_tree_logged(user_tree):
    client = APIClient()
    refresh = RefreshToken.for_user(user_tree)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client, user_tree


@pytest.fixture
def category_books(db):
    return Category.objects.create(name="Books")


@pytest.fixture
def category_car(db):
    return Category.objects.create(name="Cars")


@pytest.fixture
def condition_new(db):
    return Condition.objects.create(name="Новый")


@pytest.fixture
def condition_old(db):
    return Condition.objects.create(name="Б/У")


@pytest.fixture
def ad_one(db, user_one, condition_new, category_car):
    return Ad.objects.create(
        user=user_one,
        title="car",
        description="black car",
        category=category_car,
        condition=condition_new,
    )


@pytest.fixture
def ad_two(db, user_two, condition_old, category_books):
    return Ad.objects.create(
        user=user_two,
        title="Book",
        description="The Horus Heresy",
        category=category_books,
        condition=condition_old,
    )


@pytest.fixture
def ad_tree(db, user_tree, condition_new, category_books):
    return Ad.objects.create(
        user=user_tree,
        title="Book_two",
        description="Black_imperium",
        category=category_books,
        condition=condition_new,
    )


@pytest.fixture
def ad_four(db, user_one, condition_new, category_car):
    return Ad.objects.create(
        user=user_one,
        title="dog",
        description="white dog",
        category=category_car,
        condition=condition_new,
    )


@pytest.fixture
def exchange_status_waiting(db):
    return ExchangeStatus.objects.create(status="Ожидание")


@pytest.fixture
def exchange_status_accepted(db):
    return ExchangeStatus.objects.create(status="Принято")


@pytest.fixture
def exchange_one(
    db,
    ad_one,
    ad_two,
    exchange_status_waiting,
):
    return Exchange.objects.create(
        ad_sender=ad_one,
        ad_receiver=ad_two,
        comment="test comment #1",
        status=exchange_status_waiting,
    )


@pytest.fixture
def exchange_two(db, ad_tree, ad_one, exchange_status_accepted):
    return Exchange.objects.create(
        ad_sender=ad_tree,
        ad_receiver=ad_one,
        comment="test comment #2",
        status=exchange_status_accepted,
    )
