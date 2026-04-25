from django.contrib import admin
from .models import Category, Habit


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'created_at']
    list_editable = ['is_active']


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_name', 'category', 'duration', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['user__username', 'activity_name']