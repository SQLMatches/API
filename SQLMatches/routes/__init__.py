# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from starlette.routing import Mount, Route

from .match import MatchCreateRoute, MatchScoreboardRoute


ROUTES = [
    Mount("/api", routes=[
        Mount("/match", routes=[
            Route("/create", MatchCreateRoute),
            Route("/{match_id}", MatchScoreboardRoute)
        ])
    ])
]


ERROR_HANDLERS = []
