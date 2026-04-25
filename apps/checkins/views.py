from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Mood, CheckIn
from .serializers import (
    MoodSerializer, CheckInSerializer, CheckInSummarySerializer,
    AdminMoodSerializer, AdminCheckInSerializer,
)
from apps.core.permissions import IsAdminRole
from django.utils import timezone
import datetime
from apps.accounts.models import User


# ── Public/User Views ─────────────────────────────────────────

class MoodListView(generics.ListAPIView):
    """Active moods for the mobile picker."""
    queryset = Mood.objects.filter(is_active=True)
    serializer_class = MoodSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckInCreateView(generics.CreateAPIView):
    serializer_class = CheckInSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckInHistoryView(generics.ListAPIView):
    """User's own check-in history with optional period filter."""
    serializer_class = CheckInSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = CheckIn.objects.filter(user=self.request.user)
        period = self.request.query_params.get('period')  # weekly / monthly / yearly
        if period == 'weekly':
            qs = qs.filter(created_at__week=self._current_week())
        elif period == 'monthly':
            qs = qs.filter(created_at__month=self._current_month(),
                           created_at__year=self._current_year())
        elif period == 'yearly':
            qs = qs.filter(created_at__year=self._current_year())
        return qs

    def _current_week(self):
        from django.utils import timezone
        return timezone.now().isocalendar()[1]

    def _current_month(self):
        from django.utils import timezone
        return timezone.now().month

    def _current_year(self):
        from django.utils import timezone
        return timezone.now().year


class CheckInDetailView(generics.RetrieveAPIView):
    serializer_class = CheckInSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CheckIn.objects.filter(user=self.request.user)


class DashboardStatsView(APIView):
    """
    Returns aggregated scores for the home dashboard:
    - Latest check-in scores
    - 7-day average heart balance trend
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        latest = CheckIn.objects.filter(user=user).first()
        averages = CheckIn.objects.filter(user=user).aggregate(
            avg_mental=Avg('mental_clarity'),
            avg_emotional=Avg('emotional_balance'),
            avg_spiritual=Avg('spiritual_wellness'),
            avg_physical=Avg('physical_energy'),
            avg_heart_balance=Avg('heart_balance_score'),
            total_checkins=Count('id'),
        )

        # Last 7 daily averages for the trend chart
        seven_days_ago = timezone.now() - datetime.timedelta(days=7)
        trend = (
            CheckIn.objects
            .filter(user=user, created_at__gte=seven_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(avg_score=Avg('heart_balance_score'))
            .order_by('date')
        )

        return Response({
            'latest': CheckInSerializer(latest).data if latest else None,
            'averages': averages,
            'trend': list(trend),
        })


# ── Admin Views ───────────────────────────────────────────────

class AdminMoodListCreateView(generics.ListCreateAPIView):
    queryset = Mood.objects.all().order_by('name')
    serializer_class = AdminMoodSerializer
    permission_classes = [IsAdminRole]


class AdminMoodDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mood.objects.all()
    serializer_class = AdminMoodSerializer
    permission_classes = [IsAdminRole]


class AdminCheckInListView(generics.ListAPIView):
    queryset = CheckIn.objects.select_related('user', 'mood').order_by('-created_at')
    serializer_class = AdminCheckInSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'mood']
    ordering_fields = ['created_at', 'heart_balance_score']


class AdminCheckInDetailView(generics.RetrieveDestroyAPIView):
    queryset = CheckIn.objects.all()
    serializer_class = AdminCheckInSerializer
    permission_classes = [IsAdminRole]


class AdminDashboardView(APIView):
    """
    Admin dashboard stats:
    - Heart balance trend across ALL users
    - Mood distribution across ALL users
    - User insights (total, active, pro)
    """
    permission_classes = [IsAdminRole]

    def get(self, request):

        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)

        trend = (
            CheckIn.objects
            .filter(created_at__gte=thirty_days_ago)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(avg_score=Avg('heart_balance_score'))
            .order_by('date')
        )

        mood_distribution = (
            CheckIn.objects
            .filter(created_at__gte=thirty_days_ago)
            .values('mood__name', 'mood__emoji')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        user_insights = User.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(is_active=True)),
            pro=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(plan='pro')),
        )

        return Response({
            'heart_balance_trend': list(trend),
            'mood_distribution': list(mood_distribution),
            'user_insights': user_insights,
        })