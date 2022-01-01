from falcon import asgi

from .serializers import json_serialize


APP = asgi.App()
APP.set_error_serializer(json_serialize)
