from rest_framework.routers import DefaultRouter

from .views import api_views


router = DefaultRouter()
router.register(
    r"сategory",
    api_views.CategoryViewSet,
    basename="сategory",
)
router.register(
    r"condition",
    api_views.ConditionListViewSet,
    basename="condition",
)
router.register(
    r"ads",
    api_views.AdViewSet,
    basename="ads"
)
router.register(
    r"exchange",
    api_views.AdExchangeViewSet,
    basename="exchange"
)
