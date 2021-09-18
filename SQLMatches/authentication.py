import base64
import binascii

from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    AuthCredentials
)


AUTH_ERROR = "Invalid basic auth credentials"


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'basic':
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError(AUTH_ERROR)

        username, _, password = decoded.partition(":")

        # TODO: Implement auth validation and api scopes

        temp_scopes = [
            "match.create",
            "match.scoreboard"
        ]

        return AuthCredentials(temp_scopes), SimpleUser(username)
