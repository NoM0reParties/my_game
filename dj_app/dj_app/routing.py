from channels.routing import ProtocolTypeRouter, URLRouter
import quiz.routing

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        quiz.routing.websocket_urlpatterns
    )
})