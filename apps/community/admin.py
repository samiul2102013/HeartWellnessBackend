from django.contrib import admin
from .models import CommunityMessage, DirectMessage


@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'content', 'created_at']
    search_fields = ['sender__username', 'content']


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username']