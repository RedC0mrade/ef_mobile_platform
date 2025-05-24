
from django import forms
from django.core.exceptions import ValidationError

from .models import Ad, Category, Condition, Exchange, ExchangeStatus


class ExchangeForm(forms.ModelForm):
    class Meta:
        model = Exchange
        fields = ['ad_sender', 'ad_receiver', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Ваше сообщение для владельца товара...'
            }),
            'ad_sender': forms.Select(attrs={'class': 'form-select'}),
        }


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ["title", "description", "image_url", "category", "condition"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название товара",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Подробное описание...",
                }
            ),
            "image_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "condition": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["condition"].queryset = Condition.objects.all()

    def clean_image_url(self):
        url = self.cleaned_data["image_url"]
        if not url.startswith(("http://", "https://")):
            raise forms.ValidationError(
                "URL должен начинаться с http:// или https://"
            )
        return url
