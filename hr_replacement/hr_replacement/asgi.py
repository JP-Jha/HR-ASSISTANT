import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from test_details import consumers

# Set default Django settings module for the 'asgi' command.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_replacement.settings')

# Define the ASGI application
application = ProtocolTypeRouter({
    # HTTP protocol handled by default Django application
    "http": get_asgi_application(),
    
    # WebSocket protocol handled by the video stream consumer
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/video_stream/', consumers.VideoStreamConsumer.as_asgi()),
        ])
    ),
})
