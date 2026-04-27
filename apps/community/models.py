from django.db import models
from django.conf import settings


class CommunityMessage(models.Model):
    """Messages in the single HeartbeatHarmony community group."""
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class DirectMessage(models.Model):
    """One-to-one messages between two users."""
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'direct_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.content[:50]}"