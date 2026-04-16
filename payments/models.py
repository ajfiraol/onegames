from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Payment(models.Model):
    """Payment record for subscription verification."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    user = models.ForeignKey(
        'core.UserProfile',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('User')
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2
    )
    transaction_reference = models.CharField(
        _('Transaction Reference'),
        max_length=100,
        blank=True,
        help_text=_('Telebirr transaction ID or reference number')
    )
    screenshot = models.ImageField(
        _('Screenshot'),
        upload_to='payments/screenshots/',
        blank=True,
        null=True
    )
    note = models.TextField(_('Note'), blank=True, help_text=_('Admin notes'))
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        verbose_name=_('Verified By')
    )
    verified_at = models.DateTimeField(_('Verified At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} ({self.status})"

    def approve(self, verified_by):
        """Approve the payment and activate subscription."""
        from django.utils import timezone
        self.status = self.Status.APPROVED
        self.verified_by = verified_by
        self.verified_at = timezone.now()
        self.save()

        # Create or extend subscription
        self._create_or_extend_subscription()

    def reject(self, verified_by, note=''):
        """Reject the payment."""
        from django.utils import timezone
        self.status = self.Status.REJECTED
        self.verified_by = verified_by
        self.verified_at = timezone.now()
        self.note = note
        self.save()

    def _create_or_extend_subscription(self):
        """Create or extend user's subscription."""
        from subscriptions.models import Subscription, SubscriptionPlan
        from django.utils import timezone

        # Get or create a default plan
        plan = SubscriptionPlan.objects.filter(is_active=True).first()
        if not plan:
            return  # No active plan available

        # Check for existing active subscription
        existing = Subscription.objects.filter(
            user=self.user,
            is_active=True,
            end_date__gte=timezone.now()
        ).first()

        if existing:
            # Extend existing subscription
            existing.extend(plan.duration_days)
        else:
            # Create new subscription
            from django.utils import timezone
            end_date = timezone.now() + timezone.timedelta(days=plan.duration_days)
            Subscription.objects.create(
                user=self.user,
                plan=plan,
                end_date=end_date,
                is_active=True,
                payment_verified=True
            )