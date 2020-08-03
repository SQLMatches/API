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

from marshmallow import Schema
from webargs import fields
from webargs_starlette import use_args

from ..resources import Sessions, Config

from ..api import error_response, response
from ..api.model_convertor import scoreboard_to_dict

from ..community.exceptions import InvalidMatchID


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
    async def get(self, request):
        try:
            scoreboard = await request.state.community.match(
                request.path_params["match_id"]
            ).scoreboard()
        except InvalidMatchID:
            return error_response("InvalidMatchID")
        else:
            return response(scoreboard_to_dict(scoreboard))

    @use_args({"team_1_score": fields.Int(required=True),
               "team_2_score": fields.Int(required=True),
               "players": fields.List(fields.Nested(PlayersSchema)),
               "team_1_side": fields.Int(),
               "team_2_side": fields.Int(),
               "end": fields.Bool()})
    async def post(self, request, kwargs):
        try:
            await request.state.community.match(
                request.path_params["match_id"]
            ).update(**kwargs)
        except InvalidMatchID:
            return error_response("InvalidMatchID")
        else:
            return response()

    async def delete(self, request):
        try:
            await request.state.community.match(
                request.path_params["match_id"]
            ).end()
        except InvalidMatchID:
            return error_response("InvalidMatchID")
        else:
            return response()


class CreateMatchAPI(HTTPEndpoint):
    @use_args({"team_1_name": fields.Str(min=1, max=64, required=True),
               "team_2_name": fields.Str(min=1, max=64, required=True),
               "team_1_side": fields.Int(required=True),
               "team_2_side": fields.Int(required=True),
               "team_1_score": fields.Int(required=True),
               "team_2_score": fields.Int(required=True),
               "map_name": fields.Str(min=1, max=24, required=True)})
    async def post(self, request, kwargs):
        match = await request.state.community.create_match(**kwargs)

        return response({"match_id": match.match_id})


class DemoUploadAPI(HTTPEndpoint):
    async def post(self, request):
        match = request.state.community.match(request.path_params["match_id"])

        try:
            demo_status = await match.demo_status()
        except InvalidMatchID:
            return error_response("InvalidMatchID")
        else:
            if demo_status == 0:
                await match.set_demo_status(1)

                demo_data = b""
                async for chunk in request.stream():
                    demo_data += chunk

                if len(demo_data) > 80000000:
                    return error_response("FileToLarge")

                await Sessions.demo_bucket.upload.data(
                    data=demo_data,
                    file_name=Config.demo_pathway + "{}.dem".format(
                        match.match_id
                    )
                )

                await match.set_demo_status(2)

                return response()
            else:
                return error_response("DemoAlreadyUploaded")
