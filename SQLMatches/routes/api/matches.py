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

from marshmallow import Schema
from webargs import fields
from webargs_starlette import use_args

from .rate_limiter import LIMITER

from ...api import response
from ...api.model_convertor import scoreboard_to_dict, match_to_dict

from ...demos import Demo

from ...community.exceptions import InvalidMatchID, DemoAlreadyUploaded


class PlayersSchema(Schema):
    name = fields.Str(min=1, max=42, required=True)
    steam_id = fields.Str(min=64, max=64)
    team = fields.Int(required=True)
    alive = fields.Bool(required=True)
    ping = fields.Int(required=True)
    kills = fields.Int(required=True)
    headshots = fields.Int(required=True)
    assists = fields.Int(required=True)
    deaths = fields.Int(required=True)
    shots_fired = fields.Int(required=True)
    shots_hit = fields.Int(required=True)
    mvps = fields.Int(required=True)
    score = fields.Int(required=True)
    disconnected = fields.Bool(required=True)


class MatchAPI(HTTPEndpoint):
    @requires("authenticated")
    @LIMITER.limit("30/minute")
    async def get(self, request: Request) -> response:
        """Used to get the scoreboard for a match.

        Parameters
        ----------
        request : Request
        """

        try:
            scoreboard = await request.state.community.match(
                request.path_params["match_id"]
            ).scoreboard()
        except InvalidMatchID:
            raise
        else:
            return response(scoreboard_to_dict(scoreboard))

    @use_args({"team_1_score": fields.Int(required=True),
               "team_2_score": fields.Int(required=True),
               "players": fields.List(fields.Nested(PlayersSchema)),
               "team_1_side": fields.Int(),
               "team_2_side": fields.Int(),
               "end": fields.Bool()})
    @requires("master")
    @LIMITER.limit("30/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to update a match.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        try:
            await request.state.community.match(
                request.path_params["match_id"]
            ).update(**parameters)
        except InvalidMatchID:
            raise
        else:
            return response()

    @requires("master")
    @LIMITER.limit("30/minute")
    async def delete(self, request: Request) -> response:
        """Used to end a match.

        Parameters
        ----------
        request : Request
        """

        try:
            await request.state.community.match(
                request.path_params["match_id"]
            ).end()
        except InvalidMatchID:
            raise
        else:
            return response()


class MatchesAPI(HTTPEndpoint):
    @use_args({"search": fields.Str(), "page": fields.Int(),
               "desc": fields.Bool()})
    @requires("authenticated")
    @LIMITER.limit("30/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to list matches.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        return response([
            match_to_dict(match) async for match, _ in
            request.state.community.matches(**parameters)
        ])


class CreateMatchAPI(HTTPEndpoint):
    @use_args({"team_1_name": fields.Str(min=1, max=64, required=True),
               "team_2_name": fields.Str(min=1, max=64, required=True),
               "team_1_side": fields.Int(required=True),
               "team_2_side": fields.Int(required=True),
               "team_1_score": fields.Int(required=True),
               "team_2_score": fields.Int(required=True),
               "map_name": fields.Str(min=1, max=24, required=True)})
    @requires("master")
    @LIMITER.limit("30/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to create a match.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        match = await request.state.community.create_match(**parameters)

        return response({"match_id": match.match_id})


class DemoUploadAPI(HTTPEndpoint):
    @requires("master")
    @LIMITER.limit("30/minute")
    async def put(self, request: Request) -> response:
        """Used to upload a demo.

        Parameters
        ----------
        request : Request
        """

        match = request.state.community.match(request.path_params["match_id"])

        demo = Demo(match, request)
        if not demo.upload:
            return response()

        try:
            demo_status = await match.demo_status()
        except InvalidMatchID:
            raise
        else:
            if demo_status == 0:
                await match.set_demo_status(1)

                if await demo.upload():
                    await match.set_demo_status(2)
                else:
                    await match.set_demo_status(3)

                return response()
            else:
                raise DemoAlreadyUploaded()
