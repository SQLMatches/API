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
from starlette.background import BackgroundTask

from marshmallow import Schema, validate
from webargs import fields
from webargs_starlette import use_args

from ...webhook_pusher import WebhookPusher
from ...responses import response
from ...resources import Sessions, Config
from ...demos import Demo
from ...caches import CommunityCache, CommunitiesCache
from ...exceptions import InvalidMatchID, DemoAlreadyUploaded


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
    @requires("community")
    async def get(self, request: Request) -> response:
        """Used to get the scoreboard for a match.

        Parameters
        ----------
        request : Request
        """

        cache = CommunityCache(
            request.state.community.community_name
        ).scoreboard(request.path_params["match_id"])

        cache_get = await cache.get()
        if cache_get:
            return response(cache_get)

        try:
            scoreboard = await request.state.community.match(
                request.path_params["match_id"]
            ).scoreboard()
        except InvalidMatchID:
            raise
        else:
            data = scoreboard.scoreboard_api_schema

            await cache.set(data)

            return response(data)

    @use_args({"team_1_score": fields.Int(required=True,
                                          validates=validate.Range(0, 240)),
               "team_2_score": fields.Int(required=True,
                                          validates=validate.Range(0, 240)),
               "players": fields.List(fields.Nested(PlayersSchema),
                                      validates=validate.Length(1, 30)
                                      ),
               "team_1_side": fields.Int(validates=validate.Range(0, 1)),
               "team_2_side": fields.Int(validates=validate.Range(0, 1)),
               "end": fields.Bool()})
    @requires("master")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to update a match.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        match = request.state.community.match(
            request.path_params["match_id"]
        )

        try:
            await match.update(**parameters)
        except InvalidMatchID:
            raise
        else:
            scoreboard = await match.scoreboard()
            data = scoreboard.scoreboard_api_schema

            await ((CommunitiesCache()).matches()).expire()

            cache = CommunityCache(request.state.community.community_name)
            await (cache.matches()).expire()
            await (cache.scoreboard(request.path_params["match_id"])).set(
                data
            )

            await Sessions.websocket.emit(
                "match_update",
                scoreboard.match_api_schema,
                room="ws_room"
            )

            await Sessions.websocket.emit(
                request.path_params["match_id"],
                data,
                room="ws_room"
            )

            pusher = WebhookPusher(
                request.state.community.community_name,
                data
            )

            return response(
                background=BackgroundTask(
                    pusher.match_end if "end" in parameters
                    and parameters["end"]
                    else pusher.round_end
                )
            )

    @requires("master")
    async def delete(self, request: Request) -> response:
        """Used to end a match.

        Parameters
        ----------
        request : Request
        """

        match = request.state.community.match(
            request.path_params["match_id"]
        )

        try:
            await match.end()
        except InvalidMatchID:
            raise
        else:
            try:
                scoreboard = await match.scoreboard()
            except InvalidMatchID:
                pass
            else:
                data = scoreboard.scoreboard_api_schema

                await ((CommunitiesCache()).matches()).expire()

                cache = CommunityCache(request.state.community.community_name)
                await (cache.matches()).expire()
                await (cache.scoreboard(request.path_params["match_id"])).set(
                    data
                )

                await Sessions.websocket.emit(
                    "match_update",
                    scoreboard.match_api_schema,
                    room="ws_room"
                )

                await Sessions.websocket.emit(
                    request.path_params["match_id"],
                    data,
                    room="ws_room"
                )

                return response(
                    background=BackgroundTask(
                        WebhookPusher(
                            request.state.community.community_name,
                            data
                        ).match_end
                    )
                )

            return response()


class MatchesAPI(HTTPEndpoint):
    @use_args({"search": fields.Str(), "page": fields.Int(),
               "desc": fields.Bool(), "require_scoreboard": fields.Bool()})
    @requires("community")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to list matches.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        if not parameters:
            cache = CommunityCache(
                request.state.community.community_name
            ).matches()

            cache_get = await cache.get()
            if cache_get:
                return response(cache_get)

            data = [
                match.match_api_schema async for match, _ in
                request.state.community.matches(**parameters)
            ]

            await cache.set(data)
        else:
            data = [
                match.match_api_schema async for match, _ in
                request.state.community.matches(**parameters)
            ]

        return response(data)


class CreateMatchAPI(HTTPEndpoint):
    @use_args({"team_1_name": fields.Str(min=1, max=64, required=True),
               "team_2_name": fields.Str(min=1, max=64, required=True),
               "team_1_side": fields.Int(required=True,
                                         validates=validate.Range(0, 1)),
               "team_2_side": fields.Int(required=True,
                                         validates=validate.Range(0, 1)),
               "team_1_score": fields.Int(required=True,
                                          validates=validate.Range(0, 240)),
               "team_2_score": fields.Int(required=True,
                                          validates=validate.Range(0, 240)),
               "map_name": fields.Str(min=1, max=24, required=True)})
    @requires("master")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to create a match.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        data, match = await request.state.community.create_match(**parameters)

        await (CommunityCache(
            request.state.community.community_name
        ).matches()).expire()

        return response(
            {"match_id": match.match_id},
            background=BackgroundTask(
                WebhookPusher(
                    request.state.community.community_name,
                    data.match_api_schema
                ).match_start
            )
        )


class DemoUploadAPI(HTTPEndpoint):
    @requires("master")
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
            if demo_status != 0:
                raise DemoAlreadyUploaded()

            await match.set_demo_status(1)

            if await demo.upload():
                background_task = None

                await match.set_demo_status(2)
            else:
                background_task = BackgroundTask(
                    request.state.community.email,
                    title="SQLMatches.com, upload failed.",
                    content=("""A upload for a demo failed due to it
                    being too large. Go to the owner panel to increase
                    your max upload size!"""),
                    link_href=(
                        Config.frontend_url + "c/{}/owner#tab2".format(
                            match.community_name
                        )
                    ),
                    link_text="{}'s owner panel.".format(
                        match.community_name
                    )
                )

                await match.set_demo_status(3)

            scoreboard = await match.scoreboard()
            data = scoreboard.scoreboard_api_schema

            await (CommunityCache(
                match.community_name
            ).scoreboard(request.path_params["match_id"])).set(
                data
            )

            await Sessions.websocket.emit(
                "match_update",
                scoreboard.match_api_schema,
                room="ws_room"
            )

            await Sessions.websocket.emit(
                request.path_params["match_id"],
                data,
                room="ws_room"
            )

            return response(background=background_task)
