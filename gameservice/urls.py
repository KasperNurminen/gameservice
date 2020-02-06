from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from gameservice.views import Main, GameDetail, Register, Developer, DeveloperEdit, DeveloperCreate, DeveloperDelete, DeveloperDetails, Purchase, PaymentSuccess, PaymentFailed, emailConfirmation, Profile, activate_account
from django.conf.urls import url

urlpatterns = [
    path('', Main.as_view(), name="main"),
    path('game/<int:id>', GameDetail.as_view(), name="game"),
    path('register/', Register.as_view(), name="register"),
    path('developer/<int:pk>/edit', DeveloperEdit.as_view(), name="developer-edit"),
    path('developer/', Developer.as_view(), name='developer'),
    path('developer/<int:pk>', DeveloperDetails.as_view(),
         name="developer-details"),
    path('developer/new', DeveloperCreate.as_view(), name="developer-create"),
    path('developer/<int:pk>/delete',
         DeveloperDelete.as_view(), name="developer-delete"),
    path('purchase/<int:pk>', Purchase.as_view(), name="purchaseconfirmation"),
    path('paymentSuccess', PaymentSuccess.as_view(), name="paymentSuccess"),
    path('paymentFailed', PaymentFailed.as_view(), name="paymentFailed"),
    path('profile/', Profile.as_view(), name="profile"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate_account, name='activate'),
    path('emailconfirmation/', emailConfirmation.as_view(),
         name="emailconfirmation"),
]
