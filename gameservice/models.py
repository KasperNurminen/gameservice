from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class Game(models.Model):
    title = models.CharField(max_length=255)
    developer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    url = models.CharField(max_length=200)
    categories = models.ManyToManyField(
        'Category')

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Score(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    score = models.PositiveIntegerField()
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-score"]


class SaveData(models.Model):
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    data = models.CharField(max_length=9999)
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )


class Payment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    pid = models.CharField(max_length=64)
    sid = models.CharField(max_length=128)
