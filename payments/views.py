"""Payments app API views."""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.models import UserProfile
from .models import Payment


@require_http_methods(["GET"])
def payment_list(request):
    """List payments (admin only in production)."""
    status = request.GET.get('status')
    telegram_id = request.GET.get('telegram_id')

    payments = Payment.objects.all()

    if status:
        payments = payments.filter(status=status)
    if telegram_id:
        payments = payments.filter(user__telegram_id=telegram_id)

    data = []
    for payment in payments[:50]:
        data.append({
            'id': payment.id,
            'user_telegram_id': payment.user.telegram_id,
            'amount': float(payment.amount),
            'transaction_reference': payment.transaction_reference,
            'status': payment.status,
            'created_at': payment.created_at.isoformat(),
        })
    return JsonResponse({'payments': data})


@require_http_methods(["GET", "POST"])
def create_payment(request):
    """Create a new payment record."""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        telegram_id = data.get('telegram_id')
        amount = data.get('amount')
        reference = data.get('reference', '')

        if not telegram_id or not amount:
            return JsonResponse({'error': 'telegram_id and amount required'}, status=400)

        try:
            user = UserProfile.objects.get(telegram_id=telegram_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        payment = Payment.objects.create(
            user=user,
            amount=amount,
            transaction_reference=reference,
            status=Payment.Status.PENDING,
        )

        return JsonResponse({
            'payment': {
                'id': payment.id,
                'status': payment.status,
                'created_at': payment.created_at.isoformat(),
            }
        })

    # GET - show payment form fields
    return JsonResponse({
        'fields': ['telegram_id', 'amount', 'reference']
    })


@require_http_methods(["GET"])
def payment_detail(request, payment_id):
    """Get payment details."""
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)

    data = {
        'id': payment.id,
        'user_telegram_id': payment.user.telegram_id,
        'amount': float(payment.amount),
        'transaction_reference': payment.transaction_reference,
        'status': payment.status,
        'created_at': payment.created_at.isoformat(),
        'verified_by': payment.verified_by.username if payment.verified_by else None,
        'verified_at': payment.verified_at.isoformat() if payment.verified_at else None,
    }
    return JsonResponse({'payment': data})