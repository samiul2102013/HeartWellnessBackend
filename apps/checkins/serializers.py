from rest_framework import serializers
from .models import Mood, CheckIn


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ['id', 'name', 'emoji', 'score', 'is_active']


class CheckInSerializer(serializers.ModelSerializer):
    mood_detail = MoodSerializer(source='mood', read_only=True)

    class Meta:
        model = CheckIn
        fields = [
            'id', 'mood', 'mood_detail',
            'mental_clarity', 'emotional_balance',
            'spiritual_wellness', 'physical_energy',
            'gratitude', 'notes',
            'heart_balance_score', 'created_at',
        ]
        read_only_fields = ['id', 'heart_balance_score', 'created_at', 'mood_detail']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CheckInSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views / history."""
    mood_name = serializers.CharField(source='mood.name', read_only=True)
    mood_emoji = serializers.CharField(source='mood.emoji', read_only=True)

    class Meta:
        model = CheckIn
        fields = [
            'id', 'mood_name', 'mood_emoji',
            'heart_balance_score', 'created_at',
        ]


# ── Admin serializers ─────────────────────────────────────────

class AdminMoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = '__all__'


class AdminCheckInSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    mood_name = serializers.CharField(source='mood.name', read_only=True)

    class Meta:
        model = CheckIn
        fields = [
            'id', 'user', 'user_username', 'mood', 'mood_name',
            'mental_clarity', 'emotional_balance',
            'spiritual_wellness', 'physical_energy',
            'gratitude', 'notes', 'heart_balance_score', 'created_at',
        ]
        read_only_fields = ['heart_balance_score', 'created_at']