from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    """User profile linked to Telegram user."""
    telegram_id = models.BigIntegerField(_('Telegram ID'), unique=True, db_index=True)
    username = models.CharField(_('Username'), max_length=150, blank=True, null=True)
    first_name = models.CharField(_('First Name'), max_length=150, blank=True, null=True)
    last_name = models.CharField(_('Last Name'), max_length=150, blank=True, null=True)
    language = models.CharField(
        _('Language'),
        max_length=2,
        choices=[('en', 'English'), ('am', 'Amharic')],
        default='en'
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Is Active'), default=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.telegram_id} - {self.username or self.first_name}"

    @property
    def display_name(self):
        return self.username or self.first_name or str(self.telegram_id)

    def has_active_subscription(self):
        from subscriptions.models import Subscription
        return Subscription.objects.filter(
            user=self,
            is_active=True,
            end_date__gte=models.functions.Now()
        ).exists()

    def get_active_subscription(self):
        from subscriptions.models import Subscription
        return Subscription.objects.filter(
            user=self,
            is_active=True,
            end_date__gte=models.functions.Now()
        ).first()


class Game(models.Model):
    """Game model with bilingual content."""
    name = models.CharField(_('Name (English)'), max_length=200)
    name_amharic = models.CharField(_('Name (Amharic)'), max_length=200)
    description = models.TextField(_('Description (English)'), blank=True)
    description_amharic = models.TextField(_('Description (Amharic)'), blank=True)
    visual_guide = models.ImageField(
        _('Visual Guide'),
        upload_to='games/visual_guides/',
        blank=True,
        null=True
    )
    difficulty_level = models.PositiveIntegerField(
        _('Difficulty Level'),
        default=1,
        choices=[
            (1, '★'),
            (2, '★★'),
            (3, '★★★'),
            (4, '★★★★'),
            (5, '★★★★★'),
        ]
    )
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Game')
        verbose_name_plural = _('Games')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_name(self, language='en'):
        """Get name in the specified language."""
        if language == 'am':
            return self.name_amharic or self.name
        return self.name

    def get_description(self, language='en'):
        """Get description in the specified language."""
        if language == 'am':
            return self.description_amharic or self.description
        return self.description


class GameStrategy(models.Model):
    """Strategy content for a specific game."""
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='strategies',
        verbose_name=_('Game')
    )
    title = models.CharField(_('Title (English)'), max_length=200)
    title_amharic = models.CharField(_('Title (Amharic)'), max_length=200)
    content = models.TextField(_('Content (English)'))
    content_amharic = models.TextField(_('Content (Amharic)'))
    order = models.PositiveIntegerField(_('Order'), default=0)
    is_premium = models.BooleanField(_('Is Premium'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Game Strategy')
        verbose_name_plural = _('Game Strategies')
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.game.name} - {self.title}"

    def get_title(self, language='en'):
        if language == 'am':
            return self.title_amharic or self.title
        return self.title

    def get_content(self, language='en'):
        if language == 'am':
            return self.content_amharic or self.content
        return self.content