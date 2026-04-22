from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'

    class Plan(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'Pro'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    plan = models.CharField(max_length=10, choices=Plan.choices, default=Plan.FREE)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    @property
    def is_pro(self):
        return self.plan == self.Plan.PRO

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN