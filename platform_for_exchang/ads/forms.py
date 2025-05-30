from django import forms
from django.core.exceptions import ValidationError

from .models import Ad, Category, Condition, Exchange, ExchangeStatus


class ExchangeForm(forms.ModelForm):
    class Meta:
        model = Exchange
        fields = [
            "ad_sender",
            "ad_receiver",
            "comment",
        ]


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = [
            "title",
            "description",
            "image_url",
            "category",
            "condition",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["condition"].queryset = Condition.objects.all()

    def clean_image_url(self):
        url = self.cleaned_data["image_url"]
        if not url.startswith(("http://", "https://")):
            raise forms.ValidationError("URL должен начинаться с http:// или https://")
        return url
