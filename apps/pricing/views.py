from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import Plan, PlanFeature, Subscription
from .serializers import (
    PlanSerializer, SubscriptionSerializer, SubscribeSerializer,
    AdminPlanSerializer, AdminPlanFeatureSerializer, AdminSubscriptionSerializer,
)
from apps.core.permissions import IsAdminRole


def _expires_at(plan):
    """Calculate expiry date based on plan duration."""
    now = timezone.now()
    if plan.duration == Plan.Duration.MONTHLY:
        return now + timedelta(days=30)
    elif plan.duration == Plan.Duration.YEARLY:
        return now + timedelta(days=365)
    else:  # lifetime
        return None


# ── User / Mobile Views ───────────────────────────────────────

class PlanListView(generics.ListAPIView):
    """Pricing page — all active plans with features."""
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Plan.objects.filter(is_active=True).prefetch_related('features')


class SubscribeView(APIView):
    """
    User subscribes to a plan.
    - Cancels any existing active subscription
    - Creates new subscription
    - Upgrades user.plan to 'pro'
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
        user = request.user

        # Cancel existing active subscriptions
        Subscription.objects.filter(
            user=user, status=Subscription.Status.ACTIVE
        ).update(
            status=Subscription.Status.CANCELLED,
            cancelled_at=timezone.now()
        )

        # Create new subscription
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            status=Subscription.Status.ACTIVE,
            expires_at=_expires_at(plan),
        )

        # Upgrade user plan
        user.plan = 'pro'
        user.save(update_fields=['plan'])

        return Response({
            'detail': f'Successfully subscribed to {plan.name}.',
            'subscription': SubscriptionSerializer(subscription).data,
        }, status=status.HTTP_201_CREATED)


class MySubscriptionView(APIView):
    """Current user's active subscription."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subscription = Subscription.objects.filter(
            user=request.user, status=Subscription.Status.ACTIVE
        ).select_related('plan').first()

        if not subscription:
            return Response({
                'plan': 'free',
                'subscription': None,
            })

        # Auto-expire if past expiry date
        if not subscription.is_active:
            subscription.status = Subscription.Status.EXPIRED
            subscription.save(update_fields=['status'])
            request.user.plan = 'free'
            request.user.save(update_fields=['plan'])
            return Response({'plan': 'free', 'subscription': None})

        return Response({
            'plan': request.user.plan,
            'subscription': SubscriptionSerializer(subscription).data,
        })


class CancelSubscriptionView(APIView):
    """User cancels their active subscription."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        subscription = Subscription.objects.filter(
            user=request.user, status=Subscription.Status.ACTIVE
        ).first()

        if not subscription:
            return Response(
                {'detail': 'No active subscription found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.status = Subscription.Status.CANCELLED
        subscription.cancelled_at = timezone.now()
        subscription.save(update_fields=['status', 'cancelled_at'])

        # Downgrade user plan
        request.user.plan = 'free'
        request.user.save(update_fields=['plan'])

        return Response({'detail': 'Subscription cancelled. You have been moved to the free plan.'})


class MySubscriptionHistoryView(generics.ListAPIView):
    """All subscriptions for current user."""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(
            user=self.request.user
        ).select_related('plan').order_by('-started_at')


# ── Admin Views ───────────────────────────────────────────────

class AdminPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = AdminPlanSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return Plan.objects.annotate(
            subscriber_count=Count('subscriptions', filter=__import__('django.db.models', fromlist=['Q']).Q(subscriptions__status='active'))
        ).prefetch_related('features').order_by('price')


class AdminPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminPlanSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        from django.db.models import Q
        return Plan.objects.annotate(
            subscriber_count=Count('subscriptions', filter=Q(subscriptions__status='active'))
        ).prefetch_related('features')


class AdminPlanFeatureListCreateView(generics.ListCreateAPIView):
    serializer_class = AdminPlanFeatureSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['plan']

    def get_queryset(self):
        return PlanFeature.objects.select_related('plan').order_by('plan', 'order')


class AdminPlanFeatureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanFeature.objects.all()
    serializer_class = AdminPlanFeatureSerializer
    permission_classes = [IsAdminRole]


class AdminSubscriptionListView(generics.ListAPIView):
    serializer_class = AdminSubscriptionSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'plan']
    search_fields = ['user__username', 'user__email']

    def get_queryset(self):
        return Subscription.objects.select_related('user', 'plan').order_by('-started_at')


class AdminSubscriptionDetailView(generics.RetrieveUpdateAPIView):
    """Admin can manually change subscription status."""
    queryset = Subscription.objects.select_related('user', 'plan')
    serializer_class = AdminSubscriptionSerializer
    permission_classes = [IsAdminRole]


class AdminPricingStatsView(APIView):
    """Admin dashboard pricing stats."""
    permission_classes = [IsAdminRole]

    def get(self, request):
        from apps.accounts.models import User
        from django.db.models import Q

        total_users = User.objects.count()
        pro_users = User.objects.filter(plan='pro').count()
        free_users = User.objects.filter(plan='free').count()

        active_subs = Subscription.objects.filter(status='active').count()
        cancelled_subs = Subscription.objects.filter(status='cancelled').count()

        # Revenue per plan
        revenue_by_plan = []
        for plan in Plan.objects.filter(is_active=True):
            count = Subscription.objects.filter(plan=plan, status='active').count()
            revenue_by_plan.append({
                'plan': plan.name,
                'active_subscribers': count,
                'monthly_revenue': float(plan.price) * count if plan.duration == 'monthly' else 0,
            })

        return Response({
            'total_users': total_users,
            'pro_users': pro_users,
            'free_users': free_users,
            'active_subscriptions': active_subs,
            'cancelled_subscriptions': cancelled_subs,
            'revenue_by_plan': revenue_by_plan,
        })