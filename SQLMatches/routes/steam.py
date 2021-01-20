# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2021 WardPearce
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
from starlette.requests import Request
from starlette.responses import RedirectResponse

from re import search
from asyncio import sleep
from urllib.parse import urlencode

from ..resources import Config, Sessions


class SteamLogin(HTTPEndpoint):
    async def get(self, request: Request) -> RedirectResponse:
        paramters = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.identity":
            "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id":
            "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.mode": "checkid_setup",
            "openid.return_to": "{}steam/validate?return={}".format(
                Config.url,
                request.query_params["return"] if
                "return" in request.query_params else "/"
            ),
            "openid.realm": Config.url,
        }

        return RedirectResponse(
            "{}?{}".format(Config.steam_openid_url, urlencode(paramters))
        )


class SteamValidate(HTTPEndpoint):
    async def get(self, request: Request) -> RedirectResponse:
        params = request.query_params
        redirect = "/"

        if ("openid.ns" in params and "openid.mode" in params
            and "openid.claimed_id" in params and "openid.assoc_handle"
            and "openid.signed" in params and "openid.sig" in params
            and "openid.op_endpoint" in params and "openid.identity" in params
            and "openid.return_to" in params
                and "openid.response_nonce" in params):

            validation = {
                "openid.assoc_handle": params["openid.assoc_handle"],
                "openid.signed": params["openid.signed"],
                "openid.sig": params["openid.sig"],
                "openid.ns": params["openid.ns"],
            }

            signed = params["openid.signed"].split(",")

            for item in signed:
                item_arg = "openid.{}".format(item)

                if item_arg in params and params[item_arg] not in validation:
                    validation[item_arg] = params[item_arg]

                await sleep(0.000001)

            validation["openid.mode"] = "check_authentication"

            async with Sessions.aiohttp.post(
                    Config.steam_openid_url, data=validation) as resp:
                if resp.status == 200:
                    data = await resp.text()

                    if "is_valid:true" in data:
                        matched = search(
                            "https://steamcommunity.com/openid/id/(\\d+)",
                            params["openid.claimed_id"]
                        )

                        if matched and matched.group(1):
                            steam_id = matched.group(1)

                            request.session["steam_id"] = steam_id

                            if "return" in params:
                                redirect = params["return"]

        return RedirectResponse(redirect)


class SteamLogout(HTTPEndpoint):
    async def get(self, request: Request) -> RedirectResponse:
        request.session.pop("steam_id", None)

        return RedirectResponse("/")
