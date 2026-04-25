from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

FREE_HABIT_LIMIT = 3


class Category(models.Model):
    """Admin-managed habit categories (e.g. Fitness, Mindfulness, Sleep)."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'habit_categories'
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='habits'
    )
    activity_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'habits'
        ordering = ['-created_at']

    def clean(self):
        # Enforce free tier limit (exclude self on updates)
        if not self.pk:  # only on creation
            if not self.user.is_pro:
                existing = Habit.objects.filter(user=self.user, is_active=True).count()
                if existing >= FREE_HABIT_LIMIT:
                    raise ValidationError(
                        f"Free plan allows up to {FREE_HABIT_LIMIT} habits. Upgrade to Pro for unlimited habits."
                    )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.activity_name}"