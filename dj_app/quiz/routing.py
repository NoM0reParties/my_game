from django.urls import re_path

from quiz import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<gamename>\w+)/$', consumers.GameRoomConsumer.as_asgi())
]