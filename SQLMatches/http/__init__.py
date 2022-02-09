from falcon import asgi
from FalconSignedSessions import SignedSessions

# Request serializers
from .serializers import json_serialize

# Middlewares
from .middlewares import SessionComponent


APP = asgi.App()

APP.add_middleware(SessionComponent())
APP.add_middleware(SignedSessions())
APP.set_error_serializer(json_serialize)
