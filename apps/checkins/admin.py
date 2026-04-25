from django.contrib import admin
from .models import Mood, CheckIn


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'score', 'is_active']
    list_editable = ['is_active']


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'heart_balance_score', 'created_at']
    list_filter = ['mood', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['heart_balance_score']