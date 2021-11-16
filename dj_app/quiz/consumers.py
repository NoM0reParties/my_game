import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from users.models import CustomUser


class GameRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.gamename = self.scope['url_route']['kwargs']['gamename']
        self.game_group_name = f'game_{self.gamename}'
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data=None, byte_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        if message == 'ready':
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'block_buttons',
                    'message': 'block',
                    'username': self.scope['user'].username,
                    'user_id': self.scope['user'].id
                }
            )
        elif message == 'unlock':
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'unlock_buttons',
                    'message': 'unlocked'
                }
            )
        elif message == 'update':
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'update_buttons',
                    'message': 'updated'
                }
            )

    async def block_buttons(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id']
        }))

    async def unlock_buttons(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
        }))

    async def update_buttons(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
        }))


    def get_name(self):
        return CustomUser.objects.all()[0].username


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

