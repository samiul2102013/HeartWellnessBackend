from rest_framework import serializers
from .models import CommunityMessage, DirectMessage
from apps.accounts.models import User


class CommunityMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.ImageField(source='sender.avatar', read_only=True)

    class Meta:
        model = CommunityMessage
        fields = ['id', 'sender', 'sender_username', 'sender_avatar', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'sender_username', 'sender_avatar', 'created_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = DirectMessage
        fields = [
            'id', 'sender', 'sender_username',
            'receiver', 'receiver_username',
            'content', 'is_read', 'created_at',
        ]
        read_only_fields = ['id', 'sender', 'sender_username', 'receiver_username', 'is_read', 'created_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class UserListSerializer(serializers.ModelSerializer):
    """For DM user picker — list of other users."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar']