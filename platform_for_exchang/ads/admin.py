from django.contrib import admin
from .models import Category, Condition, Ad, ExchangeStatus, Exchange


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
    ]
    search_fields = ["name"]


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
    ]
    search_fields = ["name"]


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "user",
        "category",
        "condition",
        "created_at",
    ]
    list_filter = [
        "category",
        "condition",
    ]
    search_fields = [
        "title",
        "description",
        "user__username",
    ]


@admin.register(ExchangeStatus)
class ExchangeStatusAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "status",
    ]
    search_fields = ["status"]


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "ad_sender",
        "ad_receiver",
        "status",
        "created_at",
    ]
    list_filter = [
        "status",
        "ad_sender",
        "ad_receiver",
    ]
    search_fields = [
        "ad_sender__title",
        "ad_receiver__title",
        "status__status",
    ]
