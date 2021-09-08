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

from ..helpers.match import create_match


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
        model, _ = await create_match(**payload)
        return response(model.api_schema)
