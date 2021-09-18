# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from starlette.routing import Mount, Route
from starlette.exceptions import HTTPException

from .match import MatchCreateRoute, MatchScoreboardRoute
from .errors import server_error


ERROR_HANDLERS = {
    HTTPException: server_error
}


ROUTES = [
    Mount("/api", routes=[
        Mount("/match", routes=[
            Route("/create", MatchCreateRoute),
            Route("/{match_id}", MatchScoreboardRoute)
        ])
    ])
]
