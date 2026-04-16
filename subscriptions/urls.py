"""Subscriptions app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('my/', views.my_subscription, name='my_subscription'),
]