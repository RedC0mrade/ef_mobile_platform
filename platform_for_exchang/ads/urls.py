from django.urls import include, path
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views.register_views import RegisterView
from .views import ad_views
from .routers import router


app_name = "ads"

handler404 = 'ads.views.ad_views.custom_404_view'

schema_view = get_schema_view(
    openapi.Info(
        title="platform_for_exchang",
        default_version="v1",
        description="Документация API для проекта platform_for_exchang",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path(
        "ad/ad_incoming_requests/",
        ad_views.AdsIncomingRequestsView.as_view(),
        name="incoming_requests",
    ),
    path(
        "ad/my_offers/",
        ad_views.AdsMyOffersView.as_view(),
        name="my_offers",
    ),
    path(
        "exchange/accept/<int:pk>/",
        ad_views.accept_exchange,
        name="exchange_accept",
    ),
    path(
        "exchange/reject/<int:pk>/",
        ad_views.reject_exchange,
        name="exchange_reject",
    ),
    path(
        "exchange/delete/<int:pk>/",
        ad_views.delete_exchange,
        name="exchange_delete",
    ),
    path(
        "ad/preview/<int:pk>/",
        ad_views.ad_card_preview,
        name="ad-preview",
    ),
    path(
        "ad/create",
        ad_views.AdCreateView.as_view(),
        name="create",
    ),
    path(
        "ad/create_exchange/<int:pk>/",
        ad_views.AdCreateExchangeView.as_view(),
        name="create_exchange",
    ),
    path(
        "ad/edit/<int:pk>/",
        ad_views.AdEditView.as_view(),
        name="edit",
    ),
    path(
        "ad/delete/<int:pk>/",
        ad_views.AdDeleteView.as_view(),
        name="delete",
    ),
    path(
        "ad/detail/<int:pk>/",
        ad_views.AdDetailView.as_view(),
        name="detail",
    ),
    path(
        "ads_list/",
        ad_views.AdsListView.as_view(),
        name="list",
    ),
    path(
        "",
        ad_views.AdsIndexViews.as_view(),
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
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/token/verify/",
        TokenVerifyView.as_view(),
        name="token_verify",
    ),
    path(
        "api/",
        include(router.urls),
    ),
]
