"""Inline keyboards for the Telegram bot."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def get_language_keyboard():
    """Language selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton("🇪🇬 አማርኛ", callback_data="lang_am"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard(language='en'):
    """Main menu keyboard."""
    menu_text = {
        'en': ['🎮 Games', '📋 My Subscription', '💳 Subscribe'],
        'am': ['🎮 �AMES', '📋 የኔ ዕቃ', '💳 ቅድም ዘምን']
    }
    buttons = [
        [KeyboardButton(menu_text[language][0])],
        [KeyboardButton(menu_text[language][1])],
        [KeyboardButton(menu_text[language][2])],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_games_keyboard(games, language='en'):
    """Games list keyboard."""
    keyboard = []
    for game in games:
        btn_text = game.get_name(language)
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"game_{game.id}")])
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
    return InlineKeyboardMarkup(keyboard)


def get_subscription_plans_keyboard(plans, language='en'):
    """Subscription plans keyboard."""
    keyboard = []
    for plan in plans:
        price = plan.calculate_price()
        btn_text = f"{plan.get_name(language)} - {price:.2f} ETB"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"plan_{plan.id}")])
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
    return InlineKeyboardMarkup(keyboard)


def get_payment_keyboard(language='en'):
    """Payment confirmation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("✅ I've Paid", callback_data="payment_done"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="menu_subscribe"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscription_status_keyboard(language='en'):
    """Subscription status keyboard."""
    keyboard = [
        [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard(callback_data="menu_main", language='en'):
    """Generic back button keyboard."""
    back_text = "⬅️ Back" if language == 'en' else "⬅️ ተመለስ"
    keyboard = [[InlineKeyboardButton(back_text, callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)