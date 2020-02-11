
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView, CreateView, DeleteView
from .models import Game, Category, Payment, Score, User, SaveData
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, isDevForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
import json
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from hashlib import md5
from datetime import datetime
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core import serializers
from django.db import transaction
from django.utils.decorators import method_decorator


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


class DeveloperEdit(UserPassesTestMixin, UpdateView):
    def test_func(self):
        id = self.request.path.replace("/developer/", "").replace("/edit", "")

        return Game.objects.filter(pk=id, developer__pk=self.request.user.pk).first() or False

    model = Game
    fields = ['title', 'url', 'price', 'categories']
    template_name_suffix = '_edit'

    def get_success_url(self):
        return reverse('developer')


class DeveloperDetails(UserPassesTestMixin, View):
    def test_func(self):
        id = self.request.path.replace("/developer/", "")

        return Game.objects.filter(pk=id, developer__pk=self.request.user.pk).first() or False

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


class DeveloperDelete(UserPassesTestMixin, DeleteView):
    def test_func(self):
        id = self.request.path.replace(
            "/developer/", "").replace("/delete", "")
        return Game.objects.filter(pk=id, developer__pk=self.request.user.pk).first() or False

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

    @method_decorator(xframe_options_exempt)
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
        form2 = isDevForm()
        return render(request, 'register.html', {'form': form, 'form2': form2})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        form2 = isDevForm()

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            # add user to developer group, if checkbox is selected
            if (request.POST.get('isDeveloper') == 'on'):
                group = Group.objects.get(name='developers')
                user.groups.add(group)
            email_subject = 'Activate Your Account'
            message = render_to_string('activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            return redirect('/emailconfirmation')

        return render(request, 'register.html', {'form': form, 'form2': form2})


class Profile(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        # For highscores
        allscores = Score.objects.filter(player__pk=request.user.pk).order_by(
            '-game__title', '-score')  # sort to title and score
        gametitles = []
        for x in allscores:  # all game titles in a list
            gametitles.append(x.game.title)

        gametitles = list(dict.fromkeys(gametitles))  # remove duplicates
        finallist = []
        for title in gametitles:  # take only one score per title
            finallist.append(allscores.filter(game__title=title)[0])

        # For payment history
        allPayments = Payment.objects.filter(
            user__pk=request.user.pk)

        payment = []
        for i in allPayments:
            payment.append(i.game.title)

        payment = list(dict.fromkeys(payment))  # remove duplicates
        amount = []
        for title in payment:
            amount.append(allPayments.filter(game__title=title)[0])

        context = {
            'Highscore': finallist,
            "Amount": amount,
        }
        return render(request, "profile.html", context=context)


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/')
        # return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')


class emailConfirmation(View):

    def get(self, request, *args, **kwargs):
        return render(request, "emailconfirmation.html")


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
