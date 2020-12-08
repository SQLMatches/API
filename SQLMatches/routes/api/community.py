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

from webargs import fields
from webargs_starlette import use_args

from .rate_limiter import LIMITER

from ...community import create_community, get_community_from_owner
from ...exceptions import InvalidCommunity, NoOwnership

from ...responses import response

from ...resources import WebsocketQueue

from ...caches import CommunityCache


class CommunityOwnerAPI(HTTPEndpoint):
    @requires("is_owner")
    @LIMITER.limit("20/minute")
    async def get(self, request: Request) -> response:
        """Gets community details including secrets.

        Parameters
        ----------
        request : Request
        """

        data = {}

        cache = CommunityCache(request.state.community.community_name)
        cache_get = await cache.get()
        if cache_get:
            data["community"] = cache_get
        else:
            try:
                community = await request.state.community.get()
            except InvalidCommunity:
                raise
            else:
                data["community"] = community.community_api_schema

                await cache.set(data["community"])

        stats_cache = cache.stats()
        stats_cache_get = await stats_cache.get()
        if stats_cache_get:
            data["stats"] = stats_cache_get
        else:
            data["stats"] = (
                await request.state.community.stats()
            ).stats_api_schema

            await stats_cache.set(data["stats"])

        return response(data)

    @requires("is_owner")
    @LIMITER.limit("30/minute")
    async def delete(self, request: Request) -> response:
        """Used to disable a community.

        Parameters
        ----------
        request : Request
        """

        await request.state.community.disable()

        await CommunityCache(request.state.community.community_name).expire()

        return response()

    @requires("is_owner")
    @LIMITER.limit("10/minute")
    async def post(self, request: Request) -> response:
        """Used to regenerate a key for a community.

        Parameters
        ----------
        request : Request
        """

        return response({
            "master_api_key": await request.state.community.regenerate_master()
        })


class CommunityOwnerMatchesAPI(HTTPEndpoint):
    @use_args({"matches": fields.List(fields.String(), required=True)})
    @requires("is_owner")
    @LIMITER.limit("30/minute")
    async def delete(self, request: Request, parameters: dict) -> response:
        """Used to bulk delete matches.

        Parameters
        ----------
        request : Request
        parameters : dict

        Returns
        -------
        response
        """

        await request.state.community.delete_matches(**parameters)

        cache = CommunityCache(request.state.community.community_name)
        cache_matches = cache.matches()

        await cache.expire()
        await cache_matches.expire()

        return response()


class CommunityCreateAPI(HTTPEndpoint):
    @use_args({"community_name": fields.Str(required=True, max=32, min=4),
               "community_type": fields.Str(),
               "max_upload": fields.Float(),
               "demos": fields.Bool()})
    @requires("steam_login")
    @LIMITER.limit("10/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to create a community.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        community, _ = await create_community(
            steam_id=request.session["steam_id"],
            **parameters
        )

        WebsocketQueue.communities.append(community.api_schema)

        await CommunityCache(parameters["community_name"]).set(
            community.api_schema
        )

        return response(community.api_schema)

    @requires("steam_login")
    @LIMITER.limit("30/minute")
    async def get(self, request: Request) -> response:
        """Used to valid if user owns a community.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        try:
            community_name = (await get_community_from_owner(
                request.session["steam_id"]
            )).community_name
        except NoOwnership:
            community_name = None

        return response({
            "community_name": community_name,
            "steam_id": request.session["steam_id"]
        })
