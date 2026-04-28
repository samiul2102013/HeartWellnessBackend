from rest_framework import serializers
from .models import Plan, PlanFeature, Subscription


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ['id', 'title', 'is_included', 'order']


class PlanSerializer(serializers.ModelSerializer):
    """Public plan listing — used on mobile pricing page."""
    features = PlanFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'duration', 'is_popular',
            'features',
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.DecimalField(
        source='plan.price', max_digits=8, decimal_places=2, read_only=True
    )
    plan_duration = serializers.CharField(source='plan.duration', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_name', 'plan_price', 'plan_duration',
            'status', 'started_at', 'expires_at', 'is_active',
        ]
        read_only_fields = ['id', 'status', 'started_at', 'expires_at', 'is_active']


class SubscribeSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        try:
            plan = Plan.objects.get(id=value, is_active=True)
        except Plan.DoesNotExist:
            raise serializers.ValidationError('Plan not found or inactive.')
        return value


# ── Admin serializers ─────────────────────────────────────────

class AdminPlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ['id', 'plan', 'title', 'is_included', 'order']
        read_only_fields = ['id']


class AdminPlanSerializer(serializers.ModelSerializer):
    features = AdminPlanFeatureSerializer(many=True, read_only=True)
    subscriber_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'duration',
            'is_active', 'is_popular', 'subscriber_count', 'features',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminSubscriptionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_username', 'user_email',
            'plan', 'plan_name', 'status',
            'started_at', 'expires_at', 'cancelled_at',
        ]
        read_only_fields = ['id', 'started_at']