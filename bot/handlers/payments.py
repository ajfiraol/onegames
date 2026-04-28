"""Payment command handler."""
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from core.models import UserProfile
from subscriptions.models import SubscriptionPlan, Subscription
from payments.models import Payment
from bot.keyboards import get_back_keyboard
from bot.handlers.subscriptions import MESSAGES
from django.conf import settings


def sync_get_profile(telegram_id):
    return UserProfile.objects.get(telegram_id=telegram_id)


def sync_get_plan(plan_id):
    return SubscriptionPlan.objects.get(id=plan_id, is_active=True)


def sync_create_payment(user, amount, reference):
    return Payment.objects.create(
        user=user,
        amount=amount,
        transaction_reference=reference,
        status=Payment.Status.PENDING,
    )


async def payment_done_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment done callback - ask for transaction reference."""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    loop = asyncio.get_event_loop()

    try:
        profile = await loop.run_in_executor(None, sync_get_profile, telegram_id)
    except UserProfile.DoesNotExist:
        await query.message.reply_text("Please start with /start first!")
        return

    language = profile.language
    selected_plan_id = context.user_data.get('selected_plan_id')
    payment_amount = context.user_data.get('payment_amount')

    if not selected_plan_id or not payment_amount:
        await query.message.reply_text("No plan selected. Please select a plan first.")
        return

    # Get plan
    try:
        plan = await loop.run_in_executor(None, sync_get_plan, selected_plan_id)
    except SubscriptionPlan.DoesNotExist:
        await query.message.reply_text("Plan not found!")
        return

    # Show payment instructions with reference input
    telebirr_phone = getattr(settings, 'TELEBIRR_PHONE', '0910123456')
    min_amount = getattr(settings, 'PAYMENT_MIN_AMOUNT', 50)

    text = MESSAGES[language]['payment_info'].format(
        amount=payment_amount,
        telebirr_phone=telebirr_phone,
        min_amount=min_amount,
    )

    # Store plan info and ask for reference
    context.user_data['awaiting_reference'] = True
    context.user_data['payment_plan_id'] = selected_plan_id
    context.user_data['payment_amount'] = payment_amount

    keyboard = get_back_keyboard('menu_main', language)
    await query.message.reply_text(
        f"{text}\n\n{MESSAGES[language]['enter_reference']}",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


async def handle_payment_reference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the transaction reference input from user."""
    if not context.user_data.get('awaiting_reference'):
        return

    telegram_id = update.effective_user.id
    reference = update.message.text.strip()
    loop = asyncio.get_event_loop()

    try:
        profile = await loop.run_in_executor(None, sync_get_profile, telegram_id)
    except UserProfile.DoesNotExist:
        await update.message.reply_text("Please start with /start first!")
        return

    language = profile.language
    plan_id = context.user_data.get('payment_plan_id')
    amount = context.user_data.get('payment_amount')

    # Create payment record
    payment = await loop.run_in_executor(
        None, sync_create_payment, profile, amount, reference
    )

    # Clear user data
    context.user_data.clear()

    # Send confirmation
    text = MESSAGES[language]['payment_submitted'].format(
        amount=amount,
        reference=reference,
    )

    keyboard = get_back_keyboard('menu_main', language)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

    # Notify admins
    admin_ids = getattr(settings, 'TELEGRAM_ADMIN_IDS', [])
    notification_text = f"💰 New Payment\n\nUser: {profile.display_name}\nAmount: {amount} ETB\nReference: {reference}\n\n/payments to verify"

    for admin_id in admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=notification_text,
            )
        except Exception:
            pass