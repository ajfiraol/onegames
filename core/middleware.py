from django.utils import timezone
from django.conf import settings


class LanguageMiddleware:
    """Middleware to detect and set user language from Telegram context."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try to get language from session or user profile
        language = getattr(request, 'LANGUAGE_CODE', None)
        if not language:
            language = request.session.get('language', 'en')

        # Set for translation
        if language:
            request.LANGUAGE_CODE = language
            timezone.activate(settings.TIME_ZONE)

        response = self.get_response(request)
        return response