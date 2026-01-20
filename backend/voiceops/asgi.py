"""
ASGI config for voiceops project.
Properly routes WebSocket connections to Socket.IO and HTTP to Django.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voiceops.settings')

django_asgi_app = get_asgi_application()

from voiceops.event_handler import sio
import socketio

# To handle both WebSocket requests and other requests
async def application(scope, receive, send):
    if scope['type'] == 'websocket':
        await sio.handle_request(scope, receive, send)
    elif scope['type'] == 'http' and scope['path'].startswith('/socket.io/'):
        await sio.handle_request(scope, receive, send)
    else:
        # All other HTTP requests go to Django
        await django_asgi_app(scope, receive, send)
