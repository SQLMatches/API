# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2021 WardPearce
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


import binascii
import bcrypt
from base64 import b64decode

from typing import Tuple

from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    AuthCredentials
)
from starlette.requests import Request

from .community import (
    Community,
    api_key_to_community,
    get_community_from_owner
)
from .resources import Config
from .exceptions import InvalidAPIKey, NoOwnership


AUTH_ERROR = "Invalid basic auth credentials"


class APIAuthentication(AuthenticationBackend):
    async def authenticate(self, request: Request
                           ) -> Tuple[AuthCredentials, SimpleUser]:
        """Used to authenticate basic auth.

        Parameters
        ----------
        request : Request

        Returns
        -------
        AuthCredentials
        SimpleUser

        Raises
        ------
        AuthenticationError
        """

        if "Authorization" in request.headers:
            auth = request.headers["Authorization"]
            try:
                scheme, credentials = auth.split()
                if scheme.lower() != "basic":
                    return
                decoded = b64decode(credentials).decode("ascii")
            except (ValueError, UnicodeDecodeError, binascii.Error):
                raise AuthenticationError(AUTH_ERROR)

            username, _, password = decoded.partition(":")

            try:
                request.state.community, master = await api_key_to_community(
                    password
                )
            except InvalidAPIKey:
                raise AuthenticationError(AUTH_ERROR)
            else:
                return AuthCredentials([
                    "community", "master" if master else None
                ]), SimpleUser(username)

        elif "steam_id" in request.session:
            scopes = ["steam_login"]

            if "community_name" in request.query_params:
                scopes.append("community")

                if ("check_ownership" in request.query_params and
                        request.query_params["check_ownership"].lower()
                        == "true"):
                    try:
                        community, banned = await get_community_from_owner(
                            request.session["steam_id"]
                        )

                        if banned:
                            return

                    except NoOwnership:
                        pass
                    else:
                        if (community.community_name ==
                                request.query_params["community_name"]):
                            scopes.append("is_owner")

                request.state.community = Community(
                    request.query_params["community_name"]
                )

            if("check_root" in request.query_params and
                    request.query_params["check_root"].lower() == "true"):
                if bcrypt.checkpw(request.session["steam_id"].encode(),
                                  Config.root_steam_id_hashed):
                    scopes.append("root_login")

            return (
                AuthCredentials(scopes),
                SimpleUser(request.session["steam_id"])
            )

        elif "webhook_key" in request.query_params:
            if bcrypt.checkpw(request.query_params["webhook_key"].encode(),
                              Config.root_webhook_key_hashed):
                return (
                    AuthCredentials(["stripe_webhook"]),
                    SimpleUser("")
                )
