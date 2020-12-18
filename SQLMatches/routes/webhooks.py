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

from marshmallow import Schema, EXCLUDE
from webargs import fields
from webargs_starlette import use_args

from ..resources import Sessions
from ..responses import error_response, response


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class ObjectSchema(BaseSchema):
    id = fields.Str(required=True)
    status = fields.Str(required=True)


class DataSchema(BaseSchema):
    object = fields.Nested(ObjectSchema, required=True)


WEBHOOK_ARGS = {
    "type": fields.Str(required=True),
    "data": fields.Nested(DataSchema, required=True),
    "created": fields.Int(allow_none=True),
    "livemode": fields.Bool(allow_none=True),
    "id": fields.Str(allow_none=True),
    "object": fields.Str(allow_none=True),
    "request": fields.Dict(allow_none=True),
    "pending_webhooks": fields.Int(allow_none=True),
    "api_version": fields.Str(allow_none=True)
}


class PaymentFailed(HTTPEndpoint):
    @use_args(WEBHOOK_ARGS)
    @requires("valid_webhook")
    async def post(self, request: Request) -> response:
        return response()


class PaymentSuccess(HTTPEndpoint):
    @use_args(WEBHOOK_ARGS)
    @requires("valid_webhook")
    async def post(self, request: Request, parameters: dict) -> response:
        if parameters["type"] != "charge.succeeded":
            return error_response("charge.succeeded expected")

        await Sessions.websocket.emit(
            parameters["data"]["object"]["id"],
            {"paid": True},
            room="ws_room"
        )

        return response()
