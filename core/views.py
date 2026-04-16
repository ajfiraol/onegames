"""Core app API views."""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import UserProfile, Game, GameStrategy


@require_http_methods(["GET"])
def user_list(request):
    """List all users."""
    users = UserProfile.objects.all().values(
        'telegram_id', 'username', 'first_name', 'language', 'created_at', 'is_active'
    )
    return JsonResponse({'users': list(users)})


@require_http_methods(["GET"])
def user_detail(request, telegram_id):
    """Get user details."""
    try:
        user = UserProfile.objects.get(telegram_id=telegram_id)
        data = {
            'telegram_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language': user.language,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
            'is_active': user.is_active,
            'has_subscription': user.has_active_subscription(),
        }
        return JsonResponse({'user': data})
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@require_http_methods(["GET"])
def game_list(request):
    """List all games."""
    language = request.GET.get('language', 'en')
    games = Game.objects.filter(is_active=True)
    data = []
    for game in games:
        data.append({
            'id': game.id,
            'name': game.get_name(language),
            'description': game.get_description(language),
            'difficulty_level': game.difficulty_level,
            'visual_guide': game.visual_guide.url if game.visual_guide else None,
        })
    return JsonResponse({'games': data})


@require_http_methods(["GET"])
def game_detail(request, game_id):
    """Get game details."""
    language = request.GET.get('language', 'en')
    try:
        game = Game.objects.get(id=game_id, is_active=True)
        data = {
            'id': game.id,
            'name': game.get_name(language),
            'name_amharic': game.name_amharic,
            'description': game.get_description(language),
            'difficulty_level': game.difficulty_level,
            'visual_guide': game.visual_guide.url if game.visual_guide else None,
            'strategies_count': game.strategies.count(),
        }
        return JsonResponse({'game': data})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)


@require_http_methods(["GET"])
def game_strategies(request, game_id):
    """Get strategies for a game."""
    language = request.GET.get('language', 'en')
    telegram_id = request.GET.get('telegram_id')
    is_premium = request.GET.get('premium', 'false').lower() == 'true'

    try:
        game = Game.objects.get(id=game_id, is_active=True)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)

    user = None
    if telegram_id:
        try:
            user = UserProfile.objects.get(telegram_id=telegram_id)
        except UserProfile.DoesNotExist:
            pass

    # Check if user can access premium content
    can_access_premium = False
    if user and user.has_active_subscription():
        can_access_premium = True

    strategies = game.strategies.order_by('order')
    data = []
    for strategy in strategies:
        # Skip premium content if user doesn't have subscription
        if strategy.is_premium and not can_access_premium:
            continue

        data.append({
            'id': strategy.id,
            'title': strategy.get_title(language),
            'content': strategy.get_content(language) if (not strategy.is_premium or can_access_premium) else None,
            'is_premium': strategy.is_premium,
            'order': strategy.order,
        })
    return JsonResponse({'strategies': data})