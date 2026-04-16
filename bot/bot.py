"""Main Telegram bot entry point."""
import logging
import os
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from django.conf import settings

from bot.handlers.start import start_command, language_callback
from bot.handlers.games import games_command, game_callback
from bot.handlers.subscriptions import (
    subscribe_command,
    my_subscription_command,
    plan_callback,
)
from bot.handlers.payments import payment_done_callback, handle_payment_reference


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def create_bot():
    """Create and configure the Telegram bot application."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set in settings!")
        return None

    application = Application.builder().token(token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("games", games_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("my", my_subscription_command))

    # Register callback query handlers
    application.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(game_callback, pattern='^game_'))
    application.add_handler(CallbackQueryHandler(plan_callback, pattern='^plan_'))
    application.add_handler(CallbackQueryHandler(payment_done_callback, pattern='^payment_'))

    # Message handler for payment reference
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_payment_reference
    ))

    # Error handler
    application.add_error_handler(lambda update, context: logger.error(
        f"Error: {context.error}"
    ))

    return application


def run_bot():
    """Run the bot in polling mode."""
    app = create_bot()
    if app:
        logger.info("Starting bot polling...")
        app.run_polling(poll_interval=2)
    else:
        logger.error("Failed to create bot application")


def run_webhook(webhook_url: str):
    """Run the bot with webhook."""
    app = create_bot()
    if app:
        logger.info(f"Setting webhook to {webhook_url}...")
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get('PORT', 8443)),
            url_path="webhook",
            webhook_url=webhook_url,
        )
    else:
        logger.error("Failed to create bot application")


if __name__ == '__main__':
    run_bot()