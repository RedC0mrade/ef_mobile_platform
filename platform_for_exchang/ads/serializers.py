from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, Condition, Ad, ExchangeStatus, Exchange


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ["id", "name"]


class AdSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Ad
        fields = [
            "id",
            "user",
            "title",
            "description",
            "image_url",
            "category",
            "condition",
            "created_at",
        ]


class ExchangeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeStatus
        fields = ["id", "status"]


class ExchangeSerializer(serializers.ModelSerializer):
    ad_sender = AdSerializer(read_only=True)
    ad_receiver = AdSerializer(read_only=True)
    ad_sender_id = serializers.PrimaryKeyRelatedField(
        source="ad_sender",
        queryset=Ad.objects.all(),
        write_only=True,
    )
    ad_receiver_id = serializers.PrimaryKeyRelatedField(
        source="ad_receiver",
        queryset=Ad.objects.all(),
        write_only=True,
    )
    status = ExchangeStatusSerializer(read_only=True)

    class Meta:
        model = Exchange
        fields = [
            "id",
            "ad_sender",
            "ad_sender_id",
            "ad_receiver",
            "ad_receiver_id",
            "comment",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def validate(self, data):
        instance = Exchange(
            ad_sender=data.get("ad_sender"),
            ad_receiver=data.get("ad_receiver"),
        )
        try:
            instance.check_validity()
        except ValidationError as e:
            raise serializers.ValidationError(
                e.message_dict if hasattr(e, "message_dict") else e.messages
            )
        return data

    def create(self, validated_data):
        
        default_status, _ = ExchangeStatus.objects.get_or_create(
                status="Ожидание",
            )

        return Exchange.objects.create(
            status=default_status,
            **validated_data,
        )
