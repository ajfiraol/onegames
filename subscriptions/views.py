"""Subscriptions app API views."""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.models import UserProfile
from .models import SubscriptionPlan, Subscription


@require_http_methods(["GET"])
def plan_list(request):
    """List all subscription plans."""
    language = request.GET.get('language', 'en')
    plans = SubscriptionPlan.objects.filter(is_active=True)
    data = []
    for plan in plans:
        data.append({
            'id': plan.id,
            'name': plan.get_name(language),
            'description': plan.get_description(language),
            'base_price': float(plan.base_price),
            'price_per_extra_game': float(plan.price_per_extra_game),
            'calculated_price': float(plan.calculate_price()),
            'duration_days': plan.duration_days,
            'games_count': plan.games.count(),
        })
    return JsonResponse({'plans': data})


@require_http_methods(["GET"])
def plan_detail(request, plan_id):
    """Get subscription plan details."""
    language = request.GET.get('language', 'en')
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        data = {
            'id': plan.id,
            'name': plan.get_name(language),
            'description': plan.get_description(language),
            'base_price': float(plan.base_price),
            'calculated_price': float(plan.calculate_price()),
            'duration_days': plan.duration_days,
            'games': [
                {'id': g.id, 'name': g.get_name(language)}
                for g in plan.games.all()
            ],
        }
        return JsonResponse({'plan': data})
    except SubscriptionPlan.DoesNotExist:
        return JsonResponse({'error': 'Plan not found'}, status=404)


@require_http_methods(["GET"])
def my_subscription(request):
    """Get user's current subscription."""
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        return JsonResponse({'error': 'telegram_id required'}, status=400)

    try:
        user = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    subscription = user.get_active_subscription()
    if not subscription:
        return JsonResponse({'subscription': None})

    language = request.GET.get('language', 'en')
    data = {
        'id': subscription.id,
        'plan_name': subscription.plan.get_name(language),
        'start_date': subscription.start_date.isoformat(),
        'end_date': subscription.end_date.isoformat(),
        'is_active': subscription.is_active,
        'payment_verified': subscription.payment_verified,
    }
    return JsonResponse({'subscription': data})