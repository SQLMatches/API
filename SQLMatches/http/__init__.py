from falcon import asgi

# Request serializers
from .serializers import json_serialize

# Middlewares
from .middlewares import SessionComponent


APP = asgi.App()

APP.add_middleware(SessionComponent())
APP.set_error_serializer(json_serialize)
