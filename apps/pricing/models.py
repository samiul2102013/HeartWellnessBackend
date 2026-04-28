from django.db import models
from django.conf import settings


class Plan(models.Model):
    class Duration(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        YEARLY = 'yearly', 'Yearly'
        LIFETIME = 'lifetime', 'Lifetime'

    name = models.CharField(max_length=100)               # e.g. "Pro Monthly"
    slug = models.SlugField(unique=True)                   # e.g. "pro-monthly"
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.CharField(
        max_length=10, choices=Duration.choices, default=Duration.MONTHLY
    )
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)        # Highlighted on pricing page
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} — ${self.price}"


class PlanFeature(models.Model):
    """Features listed under each plan (e.g. 'Unlimited Habits', 'Community Access')."""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    is_included = models.BooleanField(default=True)  # False = shown as ❌ (not included)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'plan_features'
        ordering = ['order']

    def __str__(self):
        return f"{self.plan.name} — {self.title}"


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        CANCELLED = 'cancelled', 'Cancelled'
        EXPIRED = 'expired', 'Expired'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # null = lifetime
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} — {self.plan.name} — {self.status}"

    @property
    def is_active(self):
        from django.utils import timezone
        if self.status != self.Status.ACTIVE:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True