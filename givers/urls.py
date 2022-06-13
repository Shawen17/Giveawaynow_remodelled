from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/',views.subscription,name='subscription'),
    path('subscription/',views.initiate_subscription,name='initiate-subscription'),
    path('<str:ref>/subscription',views.verify_subscription,name='verify-subscription'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    ]
