"""
ASGI config for BaseGui project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

"""https://channels.readthedocs.io/en/latest/tutorial/part_2.html"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from BaseGuiApp.routing import urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BaseGui.settings')

asgi_app = get_asgi_application()

application =  ProtocolTypeRouter({
    "http"      : asgi_app,
    "websocket" : AllowedHostsOriginValidator( AuthMiddlewareStack(URLRouter(urlpatterns)) ),
})
