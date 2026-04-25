from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import Category, Habit, FREE_HABIT_LIMIT
from .serializers import (
    CategorySerializer, HabitSerializer, HabitSummarySerializer,
    AdminCategorySerializer, AdminHabitSerializer,
)
from apps.core.permissions import IsAdminRole


# ── User / Mobile Views ───────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    """Active categories for the habit creation form picker."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class HabitListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HabitSerializer
        return HabitSummarySerializer

    def get_queryset(self):
        return Habit.objects.filter(
            user=self.request.user, is_active=True
        ).select_related('category')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'habits': serializer.data,
            'count': queryset.count(),
            'limit': FREE_HABIT_LIMIT,
            'is_pro': request.user.is_pro,
            'can_create': request.user.is_pro or queryset.count() < FREE_HABIT_LIMIT,
        })


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save(update_fields=['is_active'])


# ── Admin Views ───────────────────────────────────────────────

class AdminCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminCategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(
            habit_count=Count('habits')
        ).order_by('name')


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminCategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(habit_count=Count('habits'))


class AdminHabitListView(generics.ListAPIView):
    queryset = Habit.objects.select_related('user', 'category').order_by('-created_at')
    serializer_class = AdminHabitSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['user__username', 'activity_name']