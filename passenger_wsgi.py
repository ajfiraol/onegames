"""
Passenger WSGI config for cPanel deployment
"""
import os
import sys

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onegames.settings')

# Run Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()