from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView, CreateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
import json
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .models import Game, Category, Payment, Score, SaveData
from django.contrib.auth.models import User
from django.core import serializers
from datetime import datetime
from hashlib import md5
from django.db import transaction


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
                game__pk=game.pk, user__pk=request.user.pk).first() or False
        context = {
            'searched': True,
            'results': objects,
            'query': query,
            'selected_categories': categories,
            'mygames': Payment.objects.filter(user__pk=request.user.pk),
            "categories": Category.objects.all()
        }
        return render(request, "main.html", context=context)


class Developer(PermissionRequiredMixin, View):
    permission_required = 'gameservice.can_edit_games'

    def get(self, request, *args, **kwargs):
        context = {}
        objects = Game.objects.filter(developer__pk=request.user.pk)
        for game in objects:
            payments = Payment.objects.filter(game__pk=game.pk)
            game.sold = {"count": len(payments), "monetary": sum(
                [p.price for p in payments])}

        context = {
            'results': objects
        }
        return render(request, "developer.html", context=context)


class DeveloperEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'gameservice.can_edit_games'

    model = Game
    fields = ['title', 'url', 'price', 'categories']
    template_name_suffix = '_edit'

    def get_success_url(self):
        return reverse('developer')


class DeveloperDetails(PermissionRequiredMixin, View):
    permission_required = 'gameservice.can_edit_games'

    def get(self, request, pk, *args, **kwargs):
        game = Game.objects.get(pk=pk)
        payments = Payment.objects.filter(game__pk=pk)
        total = {"count": len(payments), "monetary": sum(
            [p.price for p in payments])}
        context = {'purchases': payments,
                   'game': game,
                   'total': total}
        return render(request, "developer-details.html", context=context)


class DeveloperCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'gameservice.can_edit_games'

    model = Game
    fields = ['title', 'url', 'price', 'categories']
    template_name_suffix = '_create'

    def get_success_url(self):
        return reverse('developer')

    def form_valid(self, form):
        form.instance.developer = self.request.user
        return super().form_valid(form)


class DeveloperDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'gameservice.can_edit_games'

    model = Game
    fields = ['title', 'url', 'price', 'categories']
    template_name_suffix = '_delete'

    def get_success_url(self):
        return reverse('developer')


class GameDetail(UserPassesTestMixin, View):
    login_url = '/login/'

    def test_func(self):
        id = self.request.path.replace("/game/", "")

        return Payment.objects.filter(user__pk=self.request.user.pk, game__pk=id).first() or False

    def get(self, request, id, *args, **kwargs):
        game = Game.objects.get(pk=id)
        scores = Score.objects.filter(game=game)[0:10]
        context = {'game': game,
                   'scores': scores, }
        return render(request, "game.html", context=context)


class ScoreView(View):
    def post(self, request, id, *args, **kwargs):
        game = Game.objects.get(pk=id)
        score = request.POST.get('score', False)
        player = request.POST.get('player', False)
        prevScores = Score.objects.filter(player=player, game=game)

        if score and (len(prevScores) == 0 or int(score) > prevScores[0].score):
            # pelaajalla voi olla vain yksi highscore per peli
            with transaction.atomic():  # varmistetaan ettei kaikki scoret häviä
                prevScores.all().delete()
                newScore = Score(player=User.objects.get(pk=player), score=score,
                                 game=Game.objects.get(pk=id))
                newScore.save()
            # palauta JSONResponse jossa kaikki uudet scoret
            scores = Score.objects.filter(game=Game.objects.get(pk=id))[0:10]
            data = json.dumps(
                [{"player": score.player.username, "score": score.score} for score in scores])
            return HttpResponse(data, content_type="application/json")
        return HttpResponse(status=400)


class SaveDataView(View):
    def post(self, request, id, *args, **kwargs):
        player = request.POST.get('player', False)
        state = request.POST.get('gameState', False)
        newSave = SaveData(player=User.objects.get(pk=player),
                           data=state, game=Game.objects.get(pk=id))
        newSave.save()
        return HttpResponse(status=201)

    def get(self, request, id, *args, **kwargs):
        game = Game.objects.get(pk=id)
        pk = request.GET['player']
        gameState = SaveData.objects.filter(player__pk=pk, game=game).last()
        return JsonResponse({"data": gameState.data})


class Register(View):
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        return render(request, 'register.html', {'form': form})


class Purchase(View):

    def get(self, request, *args, **kwargs):
        # secret should not be in version control, separate file to indicate that
        with open("gameservice/secret.txt", 'r') as f:
            secret = f.read()

        id = self.kwargs.get('pk')
        game = Game.objects.get(pk=id)

        pid = str(game.pk) + "pid" + str(request.user.pk) + \
            "time" + str(datetime.timestamp(datetime.now()))
        sid = "4tNYjktBUw=="
        amount = game.price
        checksumstr = f"pid={pid:s}&sid={sid:s}&amount={amount:.2f}&token={secret:s}"
        checksum = md5(checksumstr.encode('utf-8')).hexdigest()
        context = {
            'game': game,
            'pid': pid,
            'sid': sid,
            'checksum': checksum,
            'amount': amount
        }
        return render(request, 'purchase.html', context=context)


class PaymentSuccess(View):
    def get(self, request, *args, **kwargs):
        # secret should not be in version control, separate file to indicate that
        with open("gameservice/secret.txt", 'r') as f:
            secret = f.read()

        ref = request.GET.get('ref')
        pid = request.GET.get('pid')
        result = request.GET.get('result')
        checksum1 = request.GET.get('checksum')
        checksumstr = f"pid={pid:s}&ref={ref:s}&result={result:s}&token={secret:s}"
        checksum2 = md5(checksumstr.encode('utf-8')).hexdigest()
        sid = "4tNYjktBUw=="
        game = Game.objects.get(pk=pid.split('p')[0])
        test = None
        try:  # testing if payment object already exists
            test = Payment.objects.get(pid=pid)
        except:
            test = None

        if checksum1 == checksum2 and result == 'success':  # testing that payment was succesful
            if not test:  # testing if payment object already exists
                p = Payment(user=request.user, price=game.price,
                            game=game, pid=pid, sid=sid)
                p.save()
            context = {
                'game': game
            }
            return render(request, 'paymentSuccess.html', context=context)
        else:
            return redirect("payment/error/")


class PaymentFailed(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'paymentFailed.html')
