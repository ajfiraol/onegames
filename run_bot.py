#!/usr/bin/env python
"""
Bot runner script - sets up Django before starting the bot.
"""
import os
import sys

# Set up Django before any imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onegames.settings')

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
import django
django.setup()

# Now import and run the bot
from bot.bot import run_bot

if __name__ == '__main__':
    run_bot()