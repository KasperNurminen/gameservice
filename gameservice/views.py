from django.shortcuts import render
from django.views.generic import View
from .models import Game, Category, Payment


class Main(View):
    def get(self, request, *args, **kwargs):
        context = {}
        query = request.GET.get('search', False)
        categories = request.GET.getlist('categories[]', [])
        if query != False or categories:
            objects = Game.objects.filter(title__contains=query)
            if categories:  # handle category filtering
                for category in categories:
                    for game in objects:
                        if not category in [x.name for x in game.categories.all()]:
                            objects = objects.difference(
                                Game.objects.filter(pk=game.pk))
            for game in objects:  # check whether already owned
                game.owned = Payment.objects.filter(
                    game__pk=game.pk).first() or False  # when user implemented, add here

            context = {
                'searched': True,
                'results': objects,
                'query': query,
                'selected_categories': categories,
                "categories": Category.objects.all()
            }
        return render(request, "main.html", context=context)


class GameDetail(View):
    def get(self, request, id, *args, **kwargs):

        game = Game.objects.get(pk=id)
        context = {'game': game}
        return render(request, "game.html", context=context)
