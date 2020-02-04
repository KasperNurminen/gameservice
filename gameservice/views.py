from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView, CreateView, DeleteView
from .models import Game, Category, Payment, Score, User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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

class DeveloperDetails(PermissionRequiredMixin, View):
    permission_required = 'gameservice.can_edit_games'
    def get(self, request, pk, *args, **kwargs):
        game = Game.objects.get(pk=pk)
        payments = Payment.objects.filter(game__pk=pk) 
        total = {"count": len(payments), "monetary": sum([p.price for p in payments])}
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
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
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
            #return HttpResponse('We have sent you an email, please confirm your email address to complete registration')
            return redirect('/emailconfirmation') 
            
           
        return render(request, 'register.html', {'form': form}) 


class Profile(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        allscores = Score.objects.filter(player__pk=request.user.pk).order_by('-game__title', '-score') #sort to title and score
        gametitles = []
        for x in allscores: #all game titles in a list
            gametitles.append(x.game.title)

        gametitles = list(dict.fromkeys(gametitles)) #remove duplicates
        finallist = []
        for title in gametitles: #take only one score per title
            finallist.append(allscores.filter(game__title=title)[0])
            
        print (finallist)
        context = {
            'Highscore': finallist 
                     
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
        #return HttpResponse('Your account has been activate successfully')
    else:
        return HttpResponse('Activation link is invalid!')


class emailConfirmation(View):
  
    def get(self, request, *args, **kwargs):
        return render(request, "emailconfirmation.html")
         
        
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
