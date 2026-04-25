from rest_framework import serializers
from .models import Category, Habit, FREE_HABIT_LIMIT


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_active']


class HabitSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'category', 'category_detail',
            'activity_name', 'description', 'duration',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_detail']

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        # Enforce free limit on create only
        if self.instance is None and not user.is_pro:
            active_count = Habit.objects.filter(user=user, is_active=True).count()
            if active_count >= FREE_HABIT_LIMIT:
                raise serializers.ValidationError(
                    f"Free plan allows up to {FREE_HABIT_LIMIT} habits. Upgrade to Pro for unlimited habits."
                )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HabitSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'activity_name', 'category_name',
            'category_icon', 'duration', 'is_active', 'created_at',
        ]


# ── Admin serializers ─────────────────────────────────────────

class AdminCategorySerializer(serializers.ModelSerializer):
    habit_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_active', 'habit_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminHabitSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'user_username', 'category', 'category_name',
            'activity_name', 'description', 'duration',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']