from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'price_per_extra_game', 'duration_days', 'is_active']
    list_filter = ['is_active', 'duration_days']
    search_fields = ['name', 'name_amharic']
    list_editable = ['is_active']
    filter_horizontal = ['games']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'payment_verified']
    list_filter = ['is_active', 'payment_verified', 'start_date']
    search_fields = ['user__telegram_id', 'user__username', 'plan__name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']