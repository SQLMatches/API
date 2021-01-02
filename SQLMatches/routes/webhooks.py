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
from starlette.requests import Request
from starlette.authentication import requires

from ..resources import Sessions
from ..responses import error_response, response
from ..community import stripe_customer_to_community
from ..exceptions import NoPendingPayment, InvalidCustomer


class PaymentFailed(HTTPEndpoint):
    @requires("valid_webhook")
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
            try:
                payment = await community.pending_payment()
            except NoPendingPayment:
                raise
            else:
                await community.decline_payment(payment.payment_id)

                await Sessions.websocket.emit(
                    payment.payment_id,
                    {"paid": False},
                    room="ws_room"
                )

                return response()


class PaymentSuccess(HTTPEndpoint):
    @requires("valid_webhook")
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
            try:
                payment = await community.pending_payment()
            except NoPendingPayment:
                raise
            else:
                await community.confirm_payment(
                    payment.payment_id,
                    json["data"]["object"]["receipt_url"]
                )

                await Sessions.websocket.emit(
                    payment.payment_id,
                    {"paid": True},
                    room="ws_room"
                )

                return response()
