# routing.py (in trackforge/)
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/status/<str:session_id>/", consumers.StatusConsumer.as_asgi()),
]
