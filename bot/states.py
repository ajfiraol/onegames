"""Conversation states for the Telegram bot."""
from telegram import Update
from telegram.ext import ContextTypes


class ConversationState:
    """State constants for bot conversations."""
    LANGUAGE = 1
    MAIN_MENU = 2
    GAMES_LIST = 3
    GAME_DETAIL = 4
    SUBSCRIBE_PLANS = 5
    PAYMENT_AMOUNT = 6
    PAYMENT_REFERENCE = 7
    PAYMENT_SCREENSHOT = 8
    SUBSCRIPTION_STATUS = 9
    AWAITING_PAYMENT = 10


async def set_user_state(context: ContextTypes.DEFAULT_TYPE, state: int):
    """Set the user's conversation state."""
    await context.bot_data.set(str(context._user_id), state)


async def get_user_state(context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get the user's conversation state."""
    return await context.bot_data.get(str(context._user_id), ConversationState.MAIN_MENU)


async def clear_user_state(context: ContextTypes.DEFAULT_TYPE):
    """Clear the user's conversation state."""
    await context.bot_data.delete(str(context._user_id))