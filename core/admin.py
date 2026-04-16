from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Game, GameStrategy


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'language', 'created_at', 'is_active']
    list_filter = ['language', 'is_active', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']
    list_editable = ['is_active']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_amharic', 'difficulty_level', 'is_active']
    list_filter = ['difficulty_level', 'is_active', 'created_at']
    search_fields = ['name', 'name_amharic']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GameStrategy)
class GameStrategyAdmin(admin.ModelAdmin):
    list_display = ['game', 'title', 'title_amharic', 'order', 'is_premium']
    list_filter = ['game', 'is_premium']
    search_fields = ['title', 'title_amharic']
    list_editable = ['order', 'is_premium']
    readonly_fields = ['created_at', 'updated_at']