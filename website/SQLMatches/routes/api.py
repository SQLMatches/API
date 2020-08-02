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

from webargs import fields
from webargs_starlette import use_args

from ..api import error_response, response
from ..api.model_convertor import scoreboard_to_dict

from ..community.exceptions import InvalidMatchID


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

    async def post(self, request):
        pass

    async def delete(self, request):
        pass


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
