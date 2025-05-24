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

from .mixin import UserAccesMixin
from .models import Ad, Exchange, ExchangeStatus
from .forms import AdForm, AdForm, ExchangeForm


def register_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("ads:login")
    else:
        form = UserCreationForm()
    return render(
        request=request,
        template_name="auth/register.html",
        context={"form": form},
    )

class AdsIndexViews(TemplateView):
    template_name = "ads/index.html"


class AdsListView(ListView):
    template_name = "ads/ads_list.html"
    queryset = Ad.objects.all()


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