"""Core app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/<int:telegram_id>/', views.user_detail, name='user_detail'),
    path('games/', views.game_list, name='game_list'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('games/<int:game_id>/strategies/', views.game_strategies, name='game_strategies'),
]