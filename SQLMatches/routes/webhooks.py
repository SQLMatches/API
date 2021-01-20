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
from starlette.background import BackgroundTask
from starlette.authentication import requires

from ..resources import Config
from ..responses import error_response, response
from ..community import stripe_customer_to_community
from ..exceptions import InvalidCustomer
from ..caches import CommunityCache


class PaymentFailedWebhook(HTTPEndpoint):
    @requires("stripe_webhook")
    async def post(self, request: Request) -> response:
        json = await request.json()

        if json["type"] != "charge.failed":
            return error_response("charge.failed expected")

        try:
            community = await stripe_customer_to_community(
                json["data"]["object"]["customer"]
            )
        except InvalidCustomer:
            raise
        else:
            await CommunityCache(community.community_name).expire()

            return response(background=BackgroundTask(
                community.email,
                title="SQLMatches - Payment Failed!",
                content=("""Your payment was declined! To fix this
                please go to your owner panel."""),
                link_href="{}'s owner panel".format(community.community_name),
                link_text="{}c/{}/owner#tab2".format(
                    Config.frontend_url, community.community_name
                )
            ))


class PaymentSuccessWebhook(HTTPEndpoint):
    @requires("stripe_webhook")
    async def post(self, request: Request) -> response:
        json = await request.json()

        if json["type"] != "charge.succeeded":
            return error_response("charge.succeeded expected")

        try:
            community = await stripe_customer_to_community(
                json["data"]["object"]["customer"]
            )
        except InvalidCustomer:
            raise
        else:
            await CommunityCache(community.community_name).expire()

            await community.update_subscription_expire()

            return response(background=BackgroundTask(
                community.email,
                title="SQLMatches - Invoice",
                content=("""Thanks for supporting SQLMatches,
                your receipt can be found below."""),
                link_href=json["data"]["object"]["receipt_url"],
                link_text="{}'s Receipt".format(community.community_name)
            ))
