from django.shortcuts import render, redirect
from django.views.generic import View
from .models import Game, Category, Payment, Score
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json


class Main(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        context = {}
        query = request.GET.get('search', "")
        categories = request.GET.getlist('categories[]', [])
        objects = Game.objects.filter(title__contains=query)
        if categories:  # handle category filtering
            for category in categories:
                for game in objects:
                    if not category in [x.name for x in game.categories.all()]:
                        objects = objects.difference(
                            Game.objects.filter(pk=game.pk))
        for game in objects:  # check whether already owned
            game.owned = Payment.objects.filter(
                game__pk=game.pk, user__pk=request.user.pk).first() or False  # when user implemented, add here

        context = {
            'searched': True,
            'results': objects,
            'query': query,
            'selected_categories': categories,
            "categories": Category.objects.all()
        }
        return render(request, "main.html", context=context)


class GameDetail(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request, id, *args, **kwargs):

        game = Game.objects.get(pk=id)
        context = {'game': game}
        return render(request, "game.html", context=context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        else:
            print("Form has errors")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


class Profile(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        context = {}
        #ownedgames = Payment.objects.filter(user__pk=request.user.pk)
        highscores = Score.objects.filter(player__pk=request.user.pk)
        #gamesforhighscores = 
        context = {
            'Game': highscores,
            'Highscore': highscores,
            
        }
        return render(request, "profile.html", context=context)