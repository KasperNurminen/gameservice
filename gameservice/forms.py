from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from gameservice.models import Game


class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=40, help_text='*')
    first_name = forms.CharField(max_length=40, help_text='*')
    last_name = forms.CharField(max_length=40,  help_text='*')
    email = forms.EmailField(max_length=254, help_text='*')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another Email, that is already taken')
        return email


class isDevForm(forms.Form):
    isDeveloper = forms.BooleanField(
        label='Register as game developer', required=False)

    class Meta:
        fields = ('isDeveloper')
