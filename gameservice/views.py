from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView, CreateView, DeleteView
from .models import Game, Category, Payment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import json
from django.urls import reverse
from hashlib import md5
from datetime import datetime
from django.contrib.auth.mixins import UserPassesTestMixin


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
            payments =  Payment.objects.filter(game__pk=game.pk)
            game.sold = {"count": len(payments), "monetary": sum([p.price for p in payments])}

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
        
        return Payment.objects.filter(user__pk = self.request.user.pk, game__pk = id).first() or False

    
    def get(self, request, id, *args, **kwargs):
        game = Game.objects.get(pk=id)
        context = {'game': game}
        return render(request, "game.html", context=context)


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
        #secret should not be in version control, separate file to indicate that
        with open("gameservice/secret.txt", 'r') as f:
            secret = f.read()
        
        id = self.kwargs.get('pk')
        game = Game.objects.get(pk=id)
        
        pid = str(game.pk) + "pid" + str(request.user.pk) + "time" + str(datetime.timestamp(datetime.now()))
        print(pid)
        sid = "4tNYjktBUw=="
        amount = game.price
        checksumstr =  f"pid={pid:s}&sid={sid:s}&amount={amount:.2f}&token={secret:s}"
        checksum = md5(checksumstr.encode('utf-8')).hexdigest()
        context = {
            'game': game,
            'pid' : pid,
            'sid' : sid,
            'checksum' : checksum,
            'amount' : amount
        }
        return render(request, 'purchase.html', context=context)



class PaymentSuccess(View): 
    def get(self, request, *args, **kwargs): 
        #secret should not be in version control, separate file to indicate that
        with open("gameservice/secret.txt", 'r') as f:
            secret = f.read()
        
        ref= request.GET.get('ref')
        pid = request.GET.get('pid')
        result = request.GET.get('result')
        checksum1 = request.GET.get('checksum')
        checksumstr = f"pid={pid:s}&ref={ref:s}&result={result:s}&token={secret:s}"
        checksum2 = md5(checksumstr.encode('utf-8')).hexdigest()
        sid = "4tNYjktBUw=="
        game = Game.objects.get(pk=pid.split('p')[0])
        test = None
        try: #testing if payment object already exists
            test = Payment.objects.get(pid=pid)
        except:
            test = None

        if checksum1 == checksum2 and result == 'success': #testing that payment was succesful
            if not test: #testing if payment object already exists
                p = Payment(user=request.user, price=game.price, game= game, pid = pid, sid = sid)
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