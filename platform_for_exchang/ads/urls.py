from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "ads"


urlpatterns = [
    path(
        "ad/edit/<int:pk>/",
        views.AdEditView.as_view(),
        name="edit",
    ),
    path(
        "ad/delete/<int:pk>/",
        views.AdDeleteView.as_view(),
        name="delete",
    ),
    path(
        "ad/detail/<int:pk>/",
        views.AdDetailView.as_view(),
        name="detail",
    ),
    path(
        "ads_list/",
        views.AdsListView.as_view(),
        name="list",
    ),
    path(
        "",
        views.AdsIndexViews.as_view(),
        name="index",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="auth/login.html",
            next_page="ads:index",
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="ads:login",
        ),
        name="logout",
    ),
    path(
        "register/",
        views.register_view,
        name="register",
    ),
]