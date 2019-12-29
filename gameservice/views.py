from django.shortcuts import render
from django.views.generic import View
from .models import Game


class Main(View):
    def get(self, request, *args, **kwargs):
        context = {}
        query = request.GET.get('search', False)
        if query:
            objects = Game.objects.filter(title__contains=query)
            context['searched'] = True
            context['results'] = objects
            context['query'] = query
        return render(request, "main.html", context=context)


class GameDetail(View):
    def get(self, request, id, *args, **kwargs):

        game = Game.objects.get(pk=id)
        context = {'game': game}
        return render(request, "game.html", context=context)
