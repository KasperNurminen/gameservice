from django.contrib import admin

from .models import Game


class GameAdmin(admin.ModelAdmin):
    list_display = ("title", "developer", "price", "url")


admin.site.register(Game, GameAdmin)
