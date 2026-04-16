"""Payments app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.payment_list, name='payment_list'),
    path('create/', views.create_payment, name='create_payment'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
]