from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=30,
        unique=True,
    )

    def __str__(self):
        return self.name


class Condition(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=20,
        unique=True,
    )

    def __str__(self):
        return self.name


class Ad(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ads",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(
        default="https://img.freepik.com/premium-vector/no-photo-available-vector-icon-default-image-symbol-picture-coming-soon-web-site-mobile-app_87543-18055.jpg",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="ads",
    )
    condition = models.ForeignKey(
        Condition,
        on_delete=models.PROTECT,
        related_name="ads",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Ad"

    def __str__(self):
        return f'Объявление "{self.title}" от {self.user.username}'


class ExchangeStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(
        max_length=20,
        unique=True,
    )

    def __str__(self):
        return self.status


class Exchange(models.Model):
    id = models.AutoField(primary_key=True)
    ad_sender = models.ForeignKey(
        "Ad",
        on_delete=models.CASCADE,
        related_name="sender",
    )
    ad_receiver = models.ForeignKey(
        "Ad",
        on_delete=models.CASCADE,
        related_name="receiver",
    )
    comment = models.TextField(blank=True)
    status = models.ForeignKey(
        ExchangeStatus,
        on_delete=models.PROTECT,
        related_name="proposals",
        null=False,
        blank=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ad_sender", "ad_receiver"],
                name="unique_exchange_pair",
            )
        ]

    def check_validity(self):
        if self.ad_sender == self.ad_receiver:
            raise ValidationError("Нельзя обменивать одно и то же объявление.")
        if self.ad_sender.user == self.ad_receiver.user:
            raise ValidationError(
                "Нельзя обмениваться объявлениями одного пользователя."
            )
        if Exchange.objects.filter(
            ad_sender=self.ad_receiver,
            ad_receiver=self.ad_sender,
        ).exists():
            raise ValidationError("Такой обмен уже существует.")

    def clean(self):
        self.check_validity()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Обмен от {self.ad_sender.user.username} к {self.ad_receiver.user.username} – status {self.status.status}"