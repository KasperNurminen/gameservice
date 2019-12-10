from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    title = models.CharField(max_length = 255)
    developer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=2, decimal_places=2)
    url = models.URLField(max_length=200)

class Score(models.Model):
    player = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    score =  models.PositiveIntegerField()
    game:  models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

class SaveData(models.Model):
    player = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    data =  models.CharField(max_length=9999)
    game:  models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )

class Payment(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=2, decimal_places=2)
    game:  models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )
    pid = models.CharField(max_length=64)
    sid = models.CharField(max_length=128)