from django.contrib import admin
from .models import Plan, PlanFeature, Subscription


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1
    ordering = ['order']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration', 'is_active', 'is_popular']
    list_editable = ['is_active', 'is_popular']
    inlines = [PlanFeatureInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'started_at', 'expires_at']
    list_filter = ['status', 'plan']
    search_fields = ['user__username', 'user__email']