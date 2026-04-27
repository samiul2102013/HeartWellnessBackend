from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Max, Subquery, OuterRef
from .models import CommunityMessage, DirectMessage
from .serializers import (
    CommunityMessageSerializer,
    DirectMessageSerializer,
    UserListSerializer,
)
from apps.accounts.models import User
from apps.core.permissions import IsAdminRole


# ── Community Group ───────────────────────────────────────────

class CommunityMessageHistoryView(generics.ListAPIView):
    """
    REST: Load last 50 community messages on page open.
    Real-time after that is handled by WebSocket.
    """
    serializer_class = CommunityMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CommunityMessage.objects.select_related('sender').order_by('-created_at')[:50]


# ── Direct Messages ───────────────────────────────────────────

class UserListForDMView(generics.ListAPIView):
    """
    List of all other users to start a DM with.
    Excludes the current user.
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            is_active=True
        ).exclude(id=self.request.user.id).order_by('username')


class DMHistoryView(generics.ListAPIView):
    """
    REST: Load DM history with a specific user on chat open.
    Also marks all received messages as read.
    """
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        other_id = self.kwargs['user_id']
        user = self.request.user

        # Mark received messages as read
        DirectMessage.objects.filter(
            sender_id=other_id, receiver=user, is_read=False
        ).update(is_read=True)

        return DirectMessage.objects.filter(
            Q(sender=user, receiver_id=other_id) |
            Q(sender_id=other_id, receiver=user)
        ).select_related('sender', 'receiver').order_by('created_at')


class MyConversationsView(APIView):
    """
    List of all users the current user has had a DM conversation with.
    Shows latest message per conversation — for the community page inbox.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all user IDs we've talked to
        sent_to = DirectMessage.objects.filter(sender=user).values_list('receiver_id', flat=True)
        received_from = DirectMessage.objects.filter(receiver=user).values_list('sender_id', flat=True)
        contact_ids = set(list(sent_to) + list(received_from))

        conversations = []
        for other_id in contact_ids:
            other = User.objects.filter(id=other_id).first()
            if not other:
                continue

            last_msg = DirectMessage.objects.filter(
                Q(sender=user, receiver_id=other_id) |
                Q(sender_id=other_id, receiver=user)
            ).order_by('-created_at').first()

            unread_count = DirectMessage.objects.filter(
                sender_id=other_id, receiver=user, is_read=False
            ).count()

            conversations.append({
                'user': UserListSerializer(other).data,
                'last_message': last_msg.content if last_msg else '',
                'last_message_at': last_msg.created_at if last_msg else None,
                'unread_count': unread_count,
            })

        # Sort by most recent
        conversations.sort(
            key=lambda x: x['last_message_at'] or '',
            reverse=True
        )
        return Response(conversations)


# ── Admin ─────────────────────────────────────────────────────

class AdminCommunityMessageListView(generics.ListAPIView):
    queryset = CommunityMessage.objects.select_related('sender').order_by('-created_at')
    serializer_class = CommunityMessageSerializer
    permission_classes = [IsAdminRole]


class AdminCommunityMessageDeleteView(generics.DestroyAPIView):
    queryset = CommunityMessage.objects.all()
    serializer_class = CommunityMessageSerializer
    permission_classes = [IsAdminRole]  