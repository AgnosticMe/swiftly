import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swiftly.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from swiftly.urls import websocket_urlpatterns


application = ProtocolTypeRouter({
  "http": get_asgi_application(),

  # websocket handler
  "websocket": AuthMiddlewareStack(
      URLRouter(websocket_urlpatterns)
  )
})