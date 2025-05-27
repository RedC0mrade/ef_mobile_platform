from django import forms
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    UpdateView,
)
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ads.mixin import UserAccesMixin
from ads.models import Ad, Category, Condition, Exchange, ExchangeStatus
from ads.forms import AdForm, AdForm, ExchangeForm


@login_required
def ad_card_preview(request, pk):
    """Возвращает HTML карточки объявления по ID, используется в AJAX"""
    ad = (
        Ad.objects.filter(pk=pk)
        .select_related(
            "category",
            "condition",
            "user",
        )
        .first()
    )
    if not ad:
        return JsonResponse(
            {"html": '<p class="text-danger">Объявление не найдено.</p>'}
        )

    html = render_to_string("ads/components/ad_card.html", {"ad": ad})
    return JsonResponse({"html": html})


class AdsMyOffersView(LoginRequiredMixin, ListView):
    template_name = "ads/ad_my_offers.html"
    context_object_name = "offers"

    def get_queryset(self):
        return (
            Exchange.objects.filter(
                ad_sender__user=self.request.user,
                status__status="Ожидание",
            )
            .select_related("ad_sender", "ad_receiver", "status")
            .order_by("status", "-created_at")
        )


class AdsIncomingRequestsView(LoginRequiredMixin, ListView):
    template_name = "ads/ad_incoming_requests.html"
    context_object_name = "exchanges"

    def get_queryset(self):
        return (
            Exchange.objects.filter(ad_receiver__user=self.request.user)
            .exclude(status__status="Отклонено")
            .select_related("ad_sender", "ad_receiver", "status")
            .order_by("status", "-created_at")
        )


def accept_exchange(request, pk):
    exchange = get_object_or_404(
        Exchange,
        id=pk,
        ad_receiver__user=request.user,
    )
    exchange.status, _ = ExchangeStatus.objects.get_or_create(status="Принято")
    exchange.save()
    messages.success(request, "Обмен принят!")
    return redirect("ads:incoming_requests")


def reject_exchange(request, pk):
    exchange = get_object_or_404(
        Exchange,
        id=pk,
        ad_receiver__user=request.user,
    )
    exchange.status, _ = ExchangeStatus.objects.get_or_create(
        status="Отклонено"
    )
    exchange.save()
    messages.success(request, "Обмен отклонен.")
    return redirect("ads:incoming_requests")


def delete_exchange(request, pk):
    exchange = get_object_or_404(Exchange, id=pk, ad_sender__user=request.user)

    if request.method == "POST":
        exchange.delete()
        messages.success(request, "Запрос на обмен успешно удален.")
        return redirect("ads:my_offers")

    return redirect("ads:my_offers")


class AdsIndexViews(TemplateView):
    template_name = "ads/index.html"


class AdsListView(ListView):
    template_name = "ads/ads_list.html"
    queryset = Ad.objects.all()
    paginate_by = 10
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Ad.objects.all().select_related(
            "category",
            "condition",
            "user",
        )

        search_query = self.request.GET.get("search")
        category_id = self.request.GET.get("category")
        condition_id = self.request.GET.get("condition")

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if condition_id:
            queryset = queryset.filter(condition_id=condition_id)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        context["categories"] = Category.objects.all()
        context["conditions"] = Condition.objects.all()

        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_condition'] = self.request.GET.get('condition', '')
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = "ads/ad_detail.html"


class AdDeleteView(
    UserAccesMixin,
    DeleteView,
):
    model = Ad
    success_url = reverse_lazy("ads:list")


class AdEditView(
    UserAccesMixin,
    UpdateView,
):
    model = Ad
    form_class = AdForm
    template_name = "ads/ad_edit.html"

    def get_success_url(self):
        return reverse("ads:detail", kwargs={"pk": self.object.pk})


class AdCreateView(
    LoginRequiredMixin,
    CreateView,
):
    model = Ad
    form_class = AdForm
    template_name = "ads/ad_create.html"
    success_url = reverse_lazy("ads:list")
    login_url = reverse_lazy("ads:login")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AdCreateExchangeView(LoginRequiredMixin, UserAccesMixin, CreateView):
    model = Exchange
    form_class = ExchangeForm
    template_name = "ads/ad_create_exchange.html"
    success_url = reverse_lazy("ads:my_offers")
    login_url = reverse_lazy("ads:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receiver_ad = self.get_receiver_ad()
        sender_ads = self.get_available_sender_ads(receiver_ad)

        context.update(
            {
                "ad_receiver": receiver_ad,
                "sender_ads": sender_ads,
                "default_sender_ad": sender_ads.first(),
            }
        )
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        receiver_ad = self.get_receiver_ad()

        form.fields["ad_sender"].queryset = self.get_available_sender_ads(
            receiver_ad
        )

        form.fields["ad_receiver"].initial = receiver_ad
        form.fields["ad_receiver"].widget = forms.HiddenInput()

        return form

    def get_available_sender_ads(self, receiver_ad):
        """Возвращает объявления пользователя, доступные для обмена"""

        return (
            Ad.objects.filter(user=self.request.user)
            .exclude(
                Q(sender__ad_receiver=receiver_ad)
                | Q(receiver__ad_sender=receiver_ad)
            )
            .distinct()
        )

    def get_receiver_ad(self):
        """Получает объявление-получатель с проверкой"""
        ad = get_object_or_404(Ad, pk=self.kwargs["pk"])

        if ad.user == self.request.user:
            raise PermissionDenied(
                "Нельзя обменивать свои собственные объявления"
            )

        return ad

    def form_valid(self, form):
        ad_sender = form.cleaned_data["ad_sender"]
        ad_receiver = self.get_receiver_ad()

        form.instance.ad_sender = ad_sender
        form.instance.ad_receiver = ad_receiver
        form.instance.status, _ = ExchangeStatus.objects.get_or_create(
            status="Ожидание"
        )

        print("Проверка valid:", ad_sender, ad_receiver)

        try:
            form.instance.check_validity()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

        return super().form_valid(form)

    def check_validity(self):
        if not self.ad_sender or not self.ad_receiver:
            raise ValidationError(
                "Не установлены объявления отправителя и получателя"
            )

        if self.ad_sender == self.ad_receiver:
            raise ValidationError("Нельзя обменивать объявление само на себя")
