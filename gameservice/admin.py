from django.contrib import admin

from .models import Game, Category


class GameAdmin(admin.ModelAdmin):
    fields = ("title", "developer", "price", "url", "categories")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Game, GameAdmin)
admin.site.register(Category, CategoryAdmin)
