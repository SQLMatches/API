# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.authentication import requires

from .specs import (
    API, MatchCreateSpec,
)
from .responder import response

from ..helpers.match import create_match, Match
from ..enums import TeamSides


class MatchCreateRoute(HTTPEndpoint):
    @requires("match.create")
    @API.validate(
        json=MatchCreateSpec,
        tags=["Match", "Create"]
    )
    async def post(self, request: Request) -> JSONResponse:
        """Used to create a match
        """

        payload = await request.json()
        model, _ = await create_match(
            team_1_name=payload["team_1"]["name"],
            team_2_name=payload["team_2"]["name"],
            team_1_side=TeamSides(payload["team_1"]["side"]),
            team_2_side=TeamSides(payload["team_2"]["side"]),
            team_1_score=payload["team_1"]["score"],
            team_2_score=payload["team_2"]["score"],
            map_name=payload["map"]
        )
        return response(model.api_schema)


class MatchScoreboardRoute(HTTPEndpoint):
    @requires("match.scoreboard")
    @API.validate(tags=["Match", "Scoreboard"])
    async def get(self, request: Request) -> JSONResponse:
        model = await Match(request.path_params["match_id"]).get()
        return response(model.api_schema)
