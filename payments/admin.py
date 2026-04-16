from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_reference', 'status', 'created_at', 'verified_by']
    list_filter = ['status', 'created_at']
    search_fields = ['user__telegram_id', 'user__username', 'transaction_reference']
    readonly_fields = ['user', 'amount', 'transaction_reference', 'screenshot', 'created_at', 'verified_by', 'verified_at']
    actions = ['approve_payments', 'reject_payments']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:payment_id>/approve/', self.admin_site.admin_view(self.approve_payment), name='payment_approve'),
            path('<int:payment_id>/reject/', self.admin_site.admin_view(self.reject_payment), name='payment_reject'),
        ]
        return custom_urls + urls

    def approve_payment(self, request, payment_id):
        from django.contrib.admin import site
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.approve(request.user)
            self.message_user(request, f"Payment {payment_id} approved successfully")
        except Payment.DoesNotExist:
            self.message_user(request, f"Payment {payment_id} not found", level='error')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/payments/payment/'))

    def reject_payment(self, request, payment_id):
        from django.contrib import messages
        note = request.POST.get('note', '')
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.reject(request.user, note)
            messages.success(request, f"Payment {payment_id} rejected")
        except Payment.DoesNotExist:
            messages.error(request, f"Payment {payment_id} not found")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/payments/payment/'))

    def approve_payments(self, request, queryset):
        for payment in queryset:
            payment.approve(request.user)
        self.message_user(request, f"{queryset.count()} payments approved")
    approve_payments.short_description = "Approve selected payments"

    def reject_payments(self, request, queryset):
        for payment in queryset:
            payment.reject(request.user)
        self.message_user(request, f"{queryset.count()} payments rejected")
    reject_payments.short_description = "Reject selected payments"