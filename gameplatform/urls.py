"""gameplatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from gameservice.views import Main, GameDetail, Register, Developer, DeveloperEdit, DeveloperCreate, DeveloperDelete, DeveloperDetails, Purchase, PaymentSuccess, PaymentFailed, ScoreView, SaveDataView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("django.contrib.auth.urls")),
    path('', Main.as_view(), name="main"),
    path('game/<int:id>', GameDetail.as_view(), name="game"),
    path('game/<int:id>/score', ScoreView.as_view(), name="score"),
    path('game/<int:id>/save', SaveDataView.as_view(), name="save"),
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
    path('paymentFailed', PaymentFailed.as_view(), name="paymentFailed")
]
