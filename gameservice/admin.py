from django.contrib import admin

from .models import Game, Category, Score


class GameAdmin(admin.ModelAdmin):
    fields = ("title", "developer", "price", "url", "categories")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ScoreAdmin(admin.ModelAdmin):
    list_display = ("player", "score", "game")


admin.site.register(Game, GameAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Score, ScoreAdmin)
