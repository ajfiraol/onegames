"""Start command handler."""
from telegram import Update
from telegram.ext import ContextTypes

from core.models import UserProfile
from bot.keyboards import get_language_keyboard, get_main_menu_keyboard


MESSAGES = {
    'en': {
        'welcome': "🎉 *Welcome to OneGames!* 🎉\n\nWe're your source for game strategies and tips.\n\n*Select your language to continue:*",
        'welcome_back': "*Welcome back, {name}!*\n\nWhat would you like to do?",
        'language_updated': "✅ Language set to *English*",
    },
    'am': {
        'welcome': "🎉 *እንኳዕ ናብ OneGames!* 🎉\n\nለጸድቁ ጽጋዮች እናረክብ ነን።\n\n*ቋንቋን ይምረጡ:*",
        'welcome_back': "*እንኳዕ ደህና መገብ {name}!*\n\nምን እድልዎችን?",
        'language_updated': "✅ ቋንቋን ወደ እንግሪዝኛ ተቀይረ።",
    },
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    telegram_id = user.id

    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    )

    if created:
        # New user - show language selection
        text = MESSAGES['en']['welcome']
        keyboard = get_language_keyboard()
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        # Returning user
        language = profile.language
        welcome_text = MESSAGES[language]['welcome_back'].format(
            name=profile.display_name
        )
        keyboard = get_main_menu_keyboard(language)
        await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode='Markdown')


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    telegram_id = user.id

    # Determine selected language
    data = query.data
    if data == 'lang_en':
        language = 'en'
    elif data == 'lang_am':
        language = 'am'
    else:
        language = 'en'

    # Update user profile
    profile, _ = UserProfile.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': user.username,
            'first_name': user.first_name,
        }
    )
    profile.language = language
    profile.save()

    # Send confirmation
    text = MESSAGES[language]['language_updated']
    keyboard = get_main_menu_keyboard(language)
    await query.edit_message_text(text, reply_markup=keyboard)
    await query.message.reply_text(MESSAGES[language]['welcome_back'].format(
        name=profile.display_name
    ), reply_markup=keyboard, parse_mode='Markdown')