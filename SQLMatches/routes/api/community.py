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

from webargs import fields
from webargs_starlette import use_args

from .rate_limiter import LIMITER

from ...misc import bulk_scoreboard_expire

from ...community import create_community, get_community_from_owner
from ...exceptions import InvalidCommunity, NoOwnership

from ...responses import response

from ...resources import Config, Sessions

from ...caches import CommunityCache, CommunitiesCache


class CommunityExistsAPI(HTTPEndpoint):
    @requires("community")
    @LIMITER.limit("30/minute")
    async def get(self, request: Request) -> response:
        """Used to check if community already exists.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        return response({
            "taken": await request.state.community.exists()
        })


class CommunityOwnerAPI(HTTPEndpoint):
    @requires("is_owner")
    @LIMITER.limit("30/minute")
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

        cache = CommunityCache(request.state.community.community_name)
        cache_matches = cache.matches()

        await cache.expire()
        await cache_matches.expire()

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


class CommunityPaymentAPI(HTTPEndpoint):
    @requires("is_owner")
    @LIMITER.limit("30/minute")
    async def get(self, request: Request) -> response:
        """Used to get all made payments.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        cache = CommunityCache(
            request.state.community.community_name
        ).payments()
        cache_get = await cache.get()

        if cache_get:
            return response(cache_get)

        data = [
            payment.payment_api_schema async for payment in
            request.state.community.payments()
        ]

        await cache.set(data)

        return response(data)

    @use_args({"amount": fields.Float(required=True)})
    @requires("is_owner")
    @LIMITER.limit("60/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to create a subscription.

        Parameters
        ----------
        request : Request
        parameters : dict

        Returns
        -------
        response
        """

        payment_id = await request.state.community.create_subscription(
            parameters["amount"]
        )

        await (CommunityCache(request.state.community.community_name)).expire()

        return response({"payment_id": payment_id})


class CommunityCardAPI(HTTPEndpoint):
    @use_args({"number": fields.Str(required=True),
               "exp_month": fields.Int(required=True),
               "exp_year": fields.Int(required=True),
               "cvc": fields.Int(required=True),
               "name": fields.Str(required=True)})
    @requires("is_owner")
    @LIMITER.limit("60/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to add a card.

        Parameters
        ----------
        request : Request
        parameters : dict

        Returns
        -------
        response
        """

        await request.state.community.add_card(**parameters)

        await (CommunityCache(request.state.community.community_name)).expire()

        return response()

    @requires("is_owner")
    @LIMITER.limit("60/minute")
    async def delete(self, request: Request) -> response:
        """Used to delete a card.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        await request.state.community.delete_card()

        await (CommunityCache(request.state.community.community_name)).expire()

        return response()


class CommunityUpdateAPI(HTTPEndpoint):
    @use_args({"demos": fields.Bool(), "community_type": fields.Str(),
               "match_start_webhook": fields.Str(min=5, max=255),
               "round_end_webhook": fields.Str(min=5, max=255),
               "match_end_webhook": fields.Str(min=5, max=255),
               "allow_api_access": fields.Bool(),
               "email": fields.Str(max=255)})
    @requires("is_owner")
    @LIMITER.limit("30/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        await request.state.community.update(**parameters)

        await (CommunityCache(request.state.community.community_name)).expire()

        return response()


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

        return response(background=BackgroundTask(
            bulk_scoreboard_expire,
            community_name=request.state.community.community_name,
            matches=parameters["matches"]
        ))


class CommunityCreateAPI(HTTPEndpoint):
    @use_args({"community_name": fields.Str(required=True, max=32, min=4),
               "email": fields.Str(required=True, max=255),
               "community_type": fields.Str(),
               "demos": fields.Bool(),
               "allow_api_access": fields.Bool()})
    @requires("steam_login")
    @LIMITER.limit("60/minute")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to create a community.

        Parameters
        ----------
        request : Request
        parameters : dict
        """

        model, community = await create_community(
            steam_id=request.session["steam_id"],
            **parameters
        )

        await Sessions.websocket.emit(
            "community_updates",
            model.community_api_schema,
            room="ws_room"
        )

        await CommunityCache(parameters["community_name"]).set(
            model.community_api_schema
        )
        await CommunitiesCache().expire()

        return response(model.community_api_schema, background=BackgroundTask(
            community.email,
            title=", Welcome!",
            content=("""Thanks for creating a community.
            Consider to pay for a larger max upload size on the owner panel."""),
            link_href=Config.frontend_url + "c/{}/owner#tab2".format(
                model.community_name
            ),
            link_text="{}'s owner panel.".format(model.community_name)
        ))

    @requires("steam_login")
    @LIMITER.limit("60/minute")
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
