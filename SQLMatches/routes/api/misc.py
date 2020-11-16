# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2020 WardPearce
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

from sqlalchemy import select

from ...resources import Sessions
from ...tables import update_table
from ...api import response, error_response

from .rate_limiter import LIMITER


class VersionAPI(HTTPEndpoint):
    @requires("authenticated")
    @LIMITER.limit("30/minute")
    async def get(self, request: Request) -> response:
        """Used to get a version update message.

        Parameters
        ----------
        request : Request
        """

        message = await Sessions.database.fetch_val(
            select([update_table.c.message]).select_form(
                update_table
            ).where(
                update_table.c.version >= request.path_params["version"]
            )
        )

        if message:
            return response({"message": message})
        else:
            return error_response("InvalidVersion")
