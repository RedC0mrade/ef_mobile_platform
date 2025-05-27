from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from ads.models import Ad, Category, Condition, Exchange, ExchangeStatus
from ads.serializers import (
    AdSerializer,
    CategorySerializer,
    ConditionSerializer,
    ExchangeSerializer,
)

from ads.permissions import IsOwnerOrReadOnly, IsReceiver


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ConditionListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer
    permission_classes = [permissions.AllowAny]


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "condition"]
    search_fields = ["title", "description"]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdExchangeViewSet(viewsets.ModelViewSet):
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        """
        Возвращает только обмены, связанные с объявлениями текущего пользователя
        """
        user = self.request.user
        return Exchange.objects.filter(
            Q(ad_sender__user=user) | Q(ad_receiver__user=user)
        ).distinct()

    def perform_create(self, serializer):
        """
        Проверяет права на создание обмена
        """
        ad_sender = serializer.validated_data["ad_sender"]
        ad_receiver = serializer.validated_data["ad_receiver"]

        if ad_sender.user != self.request.user:
            raise serializers.ValidationError(
                "Вы можете создавать обмен только от своего имени"
            )

        serializer.save()

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsReceiver],
    )
    def accept_exchange(self, request, pk=None):
        """Эндпоинт для принятия предложения обмена"""
        return self._change_status(pk, "Принято", request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsReceiver],
    )
    def reject_exchange(self, request, pk=None):
        """Эндпоинт для отклонения предложения обмена"""
        return self._change_status(pk, "Отклонено", request.user)

    def _change_status(self, exchange_id, new_status, user):
        """Общий метод для изменения статуса"""
        exchange = self.get_object()

        if exchange.ad_receiver.user != user:
            return Response(
                {"detail": "Предложение адресовано не вам"},
                status=status.HTTP_403_FORBIDDEN,
            )

        status_obj, _ = ExchangeStatus.objects.get_or_create(status=new_status)

        exchange.status = status_obj
        exchange.save()

        serializer = self.get_serializer(exchange)
        return Response(serializer.data)
