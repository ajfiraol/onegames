"""Subscription command handler."""
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from core.models import UserProfile
from subscriptions.models import SubscriptionPlan, Subscription
from payments.models import Payment
from bot.keyboards import (
    get_subscription_plans_keyboard,
    get_payment_keyboard,
    get_subscription_status_keyboard,
    get_back_keyboard,
)
from bot.keyboards import get_main_menu_keyboard
from django.conf import settings


MESSAGES = {
    'en': {
        'subscribe': "💳 *Subscribe*\n\nSelect a plan:",
        'no_plans': "❌ No subscription plans available at the moment.",
        'selected_plan': "📋 *Plan: {plan_name}*\n\n💰 Price: {price} ETB\n📅 Duration: {duration} days\n\n*Games included:*\n{games}",
        'payment_info': "📱 *Payment Instructions*\n\n1. Transfer *{amount} ETB* to Telebirr: *{telebirr_phone}*\n2. Enter your transaction reference below.\n\n*Note:* Minimum payment is {min_amount} ETB",
        'enter_reference': "💳 Please enter your transaction reference:",
        'payment_submitted': "✅ Payment submitted!\n\n• Amount: {amount} ETB\n• Reference: {reference}\n\nYour payment is pending verification. You'll be notified once approved.",
        'subscription_active': "📋 *Your Subscription*\n\n• Plan: {plan_name}\n• Status: Active ✅\n• Expires: {end_date}\n• Games: {games_count}",
        'no_subscription': "❌ *No Active Subscription*\n\nYou don't have an active subscription. Subscribe to access premium content!",
        'back_menu': "Returning to main menu...",
    },
    'am': {
        'subscribe': "💳 *ቅድም ዘምን*\n\nፕላን ይምረጡ:",
        'no_plans': "❌ ምን ፕላን የለም።",
        'selected_plan': "📋 *ፕላን: {plan_name}*\n\n💰 ዋጋ: {price} ETB\n📅 ጊዜ: {duration} ቀን\n\n*የሚገቡ ጸድቁ:*\n{games}",
        'payment_info': "📱 *ክፍድ መመርያ*\n\n1. *{amount} ETB* ወደ Telebirr ላክ: *{telebirr_phone}*\n2. የሚኒፈት ማስረጃ እዚህ ግባ።\n\n*ማስታወሻ:* ዝቅቲ ክፍድ {min_amount} ETB ነው",
        'enter_reference': "💳 የሚኒፈት ማስረጃ ያስገቡ:",
        'payment_submitted': "✅ ክፍድ ወደ ታላቂች!\n\n• መጠን: {amount} ETB\n• ማስረጃ: {reference}\n\nክፍድሽ ለማረጋገጥ በመጠባበት ላይ ነው።",
        'subscription_active': "📋 *የኔ ቅድም ዘምን*\n\n• ፕላን: {plan_name}\n• ሁኔታ: ንቁ ✅\n• ይጋበዛል: {end_date}\n• ጸድቁ: {games_count}",
        'no_subscription': "❌ *ምን ቅድም ዘምን የለሽ*\n\nሀን አይኖርሽ። ለማግኛ ይቅድም ዘምን!",
        'back_menu': "ወደ ዋና ምርጫ ተመለስ...",
    },
}


def sync_get_profile(telegram_id):
    return UserProfile.objects.get(telegram_id=telegram_id)


def sync_get_plans():
    return list(SubscriptionPlan.objects.filter(is_active=True))


def sync_get_plan(plan_id):
    return SubscriptionPlan.objects.get(id=plan_id, is_active=True)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command."""
    telegram_id = update.effective_user.id
    loop = asyncio.get_event_loop()

    try:
        profile = await loop.run_in_executor(None, sync_get_profile, telegram_id)
    except UserProfile.DoesNotExist:
        await update.message.reply_text("Please start with /start first!")
        return

    language = profile.language

    plans = await loop.run_in_executor(None, sync_get_plans)

    if not plans:
        await update.message.reply_text(MESSAGES[language]['no_plans'])
        return

    text = MESSAGES[language]['subscribe']
    keyboard = get_subscription_plans_keyboard(plans, language)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


async def my_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /my_subscription command."""
    telegram_id = update.effective_user.id
    loop = asyncio.get_event_loop()

    try:
        profile = await loop.run_in_executor(None, sync_get_profile, telegram_id)
    except UserProfile.DoesNotExist:
        await update.message.reply_text("Please start with /start first!")
        return

    language = profile.language
    subscription = profile.get_active_subscription()

    if subscription:
        text = MESSAGES[language]['subscription_active'].format(
            plan_name=subscription.plan.get_name(language),
            end_date=subscription.end_date.strftime('%Y-%m-%d'),
            games_count=subscription.plan.games.count(),
        )
    else:
        text = MESSAGES[language]['no_subscription']

    keyboard = get_subscription_status_keyboard(language)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


async def plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection callback."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == 'menu_main':
        await show_main_menu(update, context)
        return

    if not callback_data.startswith('plan_'):
        return

    plan_id = int(callback_data.split('_')[1])
    telegram_id = update.effective_user.id
    loop = asyncio.get_event_loop()

    profile = await loop.run_in_executor(None, sync_get_profile, telegram_id)
    language = profile.language

    try:
        plan = await loop.run_in_executor(None, sync_get_plan, plan_id)
    except SubscriptionPlan.DoesNotExist:
        await query.edit_message_text("Plan not found!")
        return

    # Calculate price
    price = plan.calculate_price()
    games_list = '\n'.join(f"• {g.get_name(language)}" for g in plan.games.all())

    # Store selected plan in user_data for payment flow
    context.user_data['selected_plan_id'] = plan_id
    context.user_data['payment_amount'] = float(price)

    text = MESSAGES[language]['selected_plan'].format(
        plan_name=plan.get_name(language),
        price=price,
        duration=plan.duration_days,
        games=games_list or "• All games",
    )

    keyboard = get_payment_keyboard(language)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu."""
    telegram_id = update.effective_user.id
    loop = asyncio.get_event_loop()

    profile = await loop.run_in_executor(None, sync_get_profile, telegram_id)
    language = profile.language

    from bot.handlers.start import start_command
    await start_command(update, context)