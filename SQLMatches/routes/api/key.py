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


from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.requests import Request

from webargs import fields
from webargs_starlette import use_args

from ...responses import response


class KeyAPI(HTTPEndpoint):
    @use_args({"api_key": fields.Str(required=True)})
    @requires("community")
    async def delete(self, request: Request, parameters: dict) -> response:
        """Used to regenerate a API key.

        Parameters
        ----------
        request : Request
        parameters : dict

        Returns
        -------
        response
        """

        return response({
            "api_key": await (
                request.state.community.key(**parameters)
            ).regenerate()
        })

    @requires(["community", "steam_login"])
    async def get(self, request: Request) -> response:
        """Used to get API key.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        key, _ = await request.state.community.user_to_key(
            request.session["steam_id"]
        )

        return response({
            "api_key": key
        })

    @requires(["community", "steam_login"])
    async def post(self, request: Request) -> response:
        """Used to create a API key.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        key, _ = await request.state.community.create_key(
            request.session["steam_id"]
        )

        return response({
            "api_key": key
        })
