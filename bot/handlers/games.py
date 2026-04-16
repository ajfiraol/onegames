"""Games command handler."""
from telegram import Update
from telegram.ext import ContextTypes

from core.models import UserProfile, Game, GameStrategy
from bot.keyboards import get_games_keyboard, get_back_keyboard


MESSAGES = {
    'en': {
        'games_list': "🎮 *Available Games*\n\nSelect a game to view strategies:",
        'game_detail': "*{name}*\n\n{difficulty}\n\n{description}",
        'no_games': "❌ No games available at the moment.",
        'strategy_section': "📝 *Strategies:*\n\n{strategies}",
        'subscribe_to_access': "🔒 Subscribe to access premium strategies!",
        'premium': "⭐ Premium",
    },
    'am': {
        'games_list': "🎮 *ጸድቁ ነቲ*\n\nምን ጸድቁ ይምረጡ:",
        'game_detail': "*{name}*\n\n{difficulty}\n\n{description}",
        'no_games': "❌ ምን ጸድቁ የለም።",
        'strategy_section': "📝 *ስትራተጺዎች:*\n\n{strategies}",
        'subscribe_to_access': "🔒 ለማግኛ ግማሽ ቅድም ዘምን!",
        'premium': "⭐ ፕሪሚየም",
    },
}


async def games_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /games command."""
    # Get user profile
    telegram_id = update.effective_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        await update.message.reply_text("Please start with /start first!")
        return

    language = profile.language
    games = Game.objects.filter(is_active=True)

    if not games.exists():
        await update.message.reply_text(MESSAGES[language]['no_games'])
        return

    text = MESSAGES[language]['games_list']
    keyboard = get_games_keyboard(games, language)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


async def game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle game selection callback."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == 'menu_main':
        from bot.handlers.start import start_command
        await start_command(update, context)
        return

    if not callback_data.startswith('game_'):
        return

    game_id = int(callback_data.split('_')[1])
    telegram_id = update.effective_user.id

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        await query.edit_message_text("Please start with /start first!")
        return

    language = profile.language

    try:
        game = Game.objects.get(id=game_id, is_active=True)
    except Game.DoesNotExist:
        await query.edit_message_text("Game not found!")
        return

    # Build game detail message
    difficulty_stars = '★' * game.difficulty_level
    description = game.get_description(language) or "No description available."

    text = MESSAGES[language]['game_detail'].format(
        name=game.get_name(language),
        difficulty=difficulty_stars,
        description=description
    )

    # Add strategies
    strategies = GameStrategy.objects.filter(game=game).order_by('order')
    if strategies.exists():
        strategy_texts = []
        for strategy in strategies:
            premium_tag = MESSAGES[language]['premium'] if strategy.is_premium else ''
            strategy_texts.append(f"{strategy.get_title(language)} {premium_tag}")

        text += MESSAGES[language]['strategy_section'].format(
            strategies='\n'.join(f"• {s}" for s in strategy_texts)
        )

        # Check subscription for premium content
        if profile.has_active_subscription():
            # Show premium content
            for strategy in strategies:
                if strategy.is_premium:
                    text += f"\n\n📌 *{strategy.get_title(language)}*:\n{strategy.get_content(language)}"
        elif not profile.has_active_subscription():
            text += f"\n\n{MESSAGES[language]['subscribe_to_access']}"

    # Add visual guide if available
    if game.visual_guide:
        text += f"\n\n📖 Visual Guide: {game.visual_guide.url}"

    keyboard = get_back_keyboard(f"back_games", language)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')