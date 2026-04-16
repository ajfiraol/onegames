from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SubscriptionPlan(models.Model):
    """Subscription plan with dynamic pricing based on number of games."""
    name = models.CharField(_('Name'), max_length=100)
    name_amharic = models.CharField(_('Name (Amharic)'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    description_amharic = models.TextField(_('Description (Amharic)'), blank=True)
    games = models.ManyToManyField(
        'core.Game',
        related_name='plans',
        verbose_name=_('Included Games'),
        blank=True
    )
    base_price = models.DecimalField(
        _('Base Price'),
        max_digits=10,
        decimal_places=2,
        default=50.00
    )
    price_per_extra_game = models.DecimalField(
        _('Price Per Extra Game'),
        max_digits=10,
        decimal_places=2,
        default=10.00
    )
    duration_days = models.PositiveIntegerField(_('Duration (Days)'), default=30)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['base_price']

    def __str__(self):
        return self.name

    def calculate_price(self):
        """Calculate price based on number of games included."""
        game_count = self.games.count()
        if game_count <= 1:
            return self.base_price
        return self.base_price + (self.price_per_extra_game * (game_count - 1))

    def get_name(self, language='en'):
        if language == 'am':
            return self.name_amharic or self.name
        return self.name

    def get_description(self, language='en'):
        if language == 'am':
            return self.description_amharic or self.description
        return self.description


class Subscription(models.Model):
    """User subscription to a plan."""
    user = models.ForeignKey(
        'core.UserProfile',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('User')
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_('Plan')
    )
    start_date = models.DateTimeField(_('Start Date'), auto_now_add=True)
    end_date = models.DateTimeField(_('End Date'))
    is_active = models.BooleanField(_('Is Active'), default=True)
    payment_verified = models.BooleanField(_('Payment Verified'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.plan.name}"

    def is_expired(self):
        from django.utils import timezone
        return self.end_date < timezone.now()

    def save(self, *args, **kwargs):
        if not self.end_date:
            from django.utils import timezone
            from django.conf import settings
            duration = getattr(settings, 'DEFAULT_SUBSCRIPTION_DAYS', 30)
            self.end_date = timezone.now() + timezone.timedelta(days=duration)
        super().save(*args, **kwargs)

    def extend(self, days):
        """Extend subscription by given days."""
        if self.end_date:
            self.end_date = self.end_date + timezone.timedelta(days=days)
        else:
            from django.utils import timezone
            self.end_date = timezone.now() + timezone.timedelta(days=days)
        self.save()