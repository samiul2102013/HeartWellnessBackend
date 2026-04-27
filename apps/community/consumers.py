import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class CommunityConsumer(AsyncWebsocketConsumer):
    """
    WebSocket for the single HeartbeatHarmony community group.
    ws://localhost:8000/ws/community/
    """
    GROUP_NAME = 'heartbeat_community'

    async def connect(self):
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            await self.close()
            return

        self.user = user
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            content = data.get('content', '').strip()
        except (json.JSONDecodeError, KeyError):
            return

        if not content:
            return

        # Save to DB
        message = await self.save_message(content)

        # Broadcast to all group members
        await self.channel_layer.group_send(
            self.GROUP_NAME,
            {
                'type': 'chat_message',
                'id': message.id,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'sender_avatar': self.user.avatar.url if self.user.avatar else None,
                'content': content,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        """Receive from group → send to WebSocket client."""
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_avatar': event['sender_avatar'],
            'content': event['content'],
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def save_message(self, content):
        from .models import CommunityMessage
        return CommunityMessage.objects.create(sender=self.user, content=content)


class DirectMessageConsumer(AsyncWebsocketConsumer):
    """
    WebSocket for one-to-one chat.
    ws://localhost:8000/ws/dm/<other_user_id>/
    Room is shared between sender and receiver using sorted IDs.
    """

    async def connect(self):
        user = self.scope.get('user')
        if not user or isinstance(user, AnonymousUser):
            await self.close()
            return

        self.user = user
        other_id = self.scope['url_route']['kwargs']['user_id']

        # Consistent room name regardless of who connects first
        ids = sorted([str(self.user.id), str(other_id)])
        self.room_name = f"dm_{'_'.join(ids)}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            content = data.get('content', '').strip()
            receiver_id = self.scope['url_route']['kwargs']['user_id']
        except (json.JSONDecodeError, KeyError):
            return

        if not content:
            return

        message = await self.save_dm(content, receiver_id)
        if not message:
            return

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'direct_message',
                'id': message.id,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'receiver_id': int(receiver_id),
                'content': content,
                'created_at': message.created_at.isoformat(),
            }
        )

    async def direct_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'receiver_id': event['receiver_id'],
            'content': event['content'],
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def save_dm(self, content, receiver_id):
        from .models import DirectMessage
        from apps.accounts.models import User
        try:
            receiver = User.objects.get(id=receiver_id)
            return DirectMessage.objects.create(
                sender=self.user,
                receiver=receiver,
                content=content,
            )
        except User.DoesNotExist:
            return None