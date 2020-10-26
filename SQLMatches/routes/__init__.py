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


from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from slowapi.errors import RateLimitExceeded

from webargs_starlette import WebargsHTTPException

# Routes
from .download import DownloadPage
from .api import MatchAPI, CreateMatchAPI, DemoUploadAPI, MatchesAPI
from .steam import SteamLogin, SteamValidate, SteamLogout
from .errors import server_error, api_error, rate_limted_error

from ..resources import Config


ERROR_HANDLERS = {
    WebargsHTTPException: api_error,
    RateLimitExceeded: rate_limted_error,
    HTTPException: server_error,
}


ROUTES = [
    Mount("/login", routes=[
        Route("/steam", SteamLogin, name="SteamLogin"),
        Route("/validate", SteamValidate),
        Route("/logout", SteamLogout, name="SteamLogout")
    ]),
    Route("/download/{match_id}", DownloadPage, name="DownloadPage"),
    Mount("/maps", StaticFiles(directory=Config.maps_dir), name="maps"),
    Mount("/api", routes=[
        Route("/matches/", MatchesAPI),
        Mount("/match", routes=[
            Route("/create/", CreateMatchAPI),
            Mount("/{match_id}", routes=[
                Route("/upload/", DemoUploadAPI),
                Route("/", MatchAPI)
            ])
        ])
    ])
]
