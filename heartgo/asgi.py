"""
ASGI config for django_test project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from heartgo import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartgo.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # Just HTTP for now. (We can add other protocols later.)
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))),
    }
)
