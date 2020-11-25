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


from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from slowapi.errors import RateLimitExceeded

from webargs_starlette import WebargsHTTPException

from ..exceptions import SQLMatchesException

# Routes
from .download import DownloadPage
from .api.matches import (
    MatchAPI,
    CreateMatchAPI,
    DemoUploadAPI,
    MatchesAPI
)
from .api.misc import VersionAPI
from .api.community import (
    CommunityOwnerAPI,
    CommunityCreateAPI
)
from .api.communities import (
    CommunitiesAPI,
    CommunityMatchesAPI,
    MatchesCommunitiesAPI
)
from .api.profile import ProfileAPI
from .api.websockets import CommunityWebsocketAPI
from .steam import SteamValidate, SteamLogin, SteamLogout
from .errors import (
    server_error,
    payload_error,
    rate_limted_error,
    internal_error
)

from ..resources import Config


ERROR_HANDLERS = {
    WebargsHTTPException: payload_error,
    RateLimitExceeded: rate_limted_error,
    HTTPException: server_error,
    SQLMatchesException: internal_error
}


ROUTES = [
    Mount("/api", routes=[
        Mount("/steam", routes=[
            Route("/login", SteamLogin),
            Route("/validate", SteamValidate),
            Route("/logout", SteamLogout)
        ]),
        Mount("/maps/", StaticFiles(directory=Config.maps_dir), name="maps"),
        Route("/matches/", MatchesAPI),  # Tested - POST @ 0.1.0
        Mount("/match", routes=[
            Route("/create/", CreateMatchAPI),  # Tested - POST @ 0.1.0
            Mount("/{match_id}", routes=[
                Route("/upload/", DemoUploadAPI),
                Route("/", MatchAPI),  # Tested - GET, POST, DELETE @ 0.1.0
                Route("/download/", DownloadPage, name="DownloadPage")
            ])
        ]),
        Route("/profile/{steam_id}/", ProfileAPI),
        Route("/version/{version}", VersionAPI),
        Mount("/community", routes=[
            Route("/owner/", CommunityOwnerAPI),
            Route("/", CommunityCreateAPI),
        ]),
        Mount("/communities", routes=[
            Route("/", CommunitiesAPI),
            Route("/matches/", CommunityMatchesAPI),
            Route("/all/", MatchesCommunitiesAPI)
        ]),
        Mount("/ws", routes=[
            WebSocketRoute("/communities/", CommunityWebsocketAPI)
        ])
    ]),
]
