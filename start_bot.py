import os
import sys
import signal

# Set up Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onegames.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

# Your bot token
os.environ['TELEGRAM_BOT_TOKEN'] = '8648394021:AAEPJ01L-egJjL4AgvIkpM_JJklPXboNIcQ'

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers.start import start_command, language_callback
from bot.handlers.games import games_command, game_callback
from bot.handlers.subscriptions import subscribe_command, my_subscription_command, plan_callback
from bot.handlers.payments import payment_done_callback, handle_payment_reference
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Creating bot application...")
    app = Application.builder().token(os.environ['TELEGRAM_BOT_TOKEN']).build()

    # Import command handlers properly
    from telegram.ext import CommandHandler

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("games", games_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("my", my_subscription_command))

    app.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    app.add_handler(CallbackQueryHandler(game_callback, pattern='^game_'))
    app.add_handler(CallbackQueryHandler(plan_callback, pattern='^plan_'))
    app.add_handler(CallbackQueryHandler(payment_done_callback, pattern='^payment_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_reference))

    logger.info("Bot ready! Starting polling...")
    app.run_polling(poll_interval=2)

if __name__ == '__main__':
    main()