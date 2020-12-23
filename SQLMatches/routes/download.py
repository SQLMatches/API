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
from starlette.requests import Request
from starlette.responses import (
    RedirectResponse,
    PlainTextResponse,
)


from ..settings import B2UploadSettings, LocalUploadSettings
from ..resources import Config


class DownloadPage(HTTPEndpoint):
    async def get(self, request: Request) -> RedirectResponse:
        """Used to redirect users to the demo download.

        Parameters
        ----------
        request : Request
        """

        if Config.upload_type == B2UploadSettings:
            return RedirectResponse(
                "{}{}{}.dem".format(
                    Config.cdn_url,
                    Config.demo_pathway,
                    request.path_params["match_id"]
                )
            )
        elif Config.upload_type == LocalUploadSettings:
            return RedirectResponse(
                "/api/demos/{}.dem".format(
                    request.path_params["match_id"]
                )
            )
        else:
            return PlainTextResponse("Demos aren't enabled!")
