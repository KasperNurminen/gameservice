from django.shortcuts import render
from django.views.generic import View
from .models import Game, Category


class Main(View):
    def get(self, request, *args, **kwargs):
        context = {"categories": Category.objects.all()}
        query = request.GET.get('search', False)
        categories = request.GET.getlist('categories[]', False)
        if query or categories:
            objects = Game.objects.filter(title__contains=query)
            print(objects)
            if categories:
                # for game in objects:
                    # for game_category in game.categories.all():
                     #   if not game_category.name in categories:
                      #      objects = objects.difference(
                       #         Game.objects.filter(pk=game.pk))
                for category in categories:
                    for game in objects:
                        print("game_categories_all", game.categories.all())
                        if not category in [x.name for x in game.categories.all()]:
                            objects = objects.difference(
                                Game.objects.filter(pk=game.pk))
            context['searched'] = True
            context['results'] = objects
            context['query'] = query
            context['selected_categories'] = categories
        return render(request, "main.html", context=context)


class GameDetail(View):
    def get(self, request, id, *args, **kwargs):

        game = Game.objects.get(pk=id)
        context = {'game': game}
        return render(request, "game.html", context=context)

        # matching = Game.objects.all()
        # if categories:
        #   matching = Game.objects.none()
        #  for category in categories:
        #     matching = matching.union(
        #        Game.objects.filter(categories__in=category))
