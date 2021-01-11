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

from ...responses import response
from ...communities import ban_communities
from ...caches import CommunitiesCache, VersionCache
from ...misc import bulk_community_expire
from ...version import Version


class CommunitiesAdminAPI(HTTPEndpoint):
    @use_args({"communities": fields.List(fields.String(), required=True)})
    @requires("root_login")
    async def delete(self, request: Request, parameters: dict) -> response:
        """Used to ban communities.

        Parameters
        ----------
        request : Request
        parameters : dict

        Returns
        -------
        response
        """

        await ban_communities(**parameters)

        await CommunitiesCache().expire()

        return response(background=BackgroundTask(
            bulk_community_expire,
            **parameters
        ))


class AdminAPI(HTTPEndpoint):
    @requires("root_login")
    async def get(self, request: Request) -> response:
        return response()

    @use_args({"major": fields.Int(required=True),
               "minor": fields.Int(required=True),
               "patch": fields.Int(required=True),
               "message": fields.String(min=6, max=64, required=True)})
    @requires("root_login")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to create or update a message.

        Parameters
        ----------
        request : Request
        parameters : dict

        Returns
        -------
        response
        """

        await Version(
            parameters["major"],
            parameters["minor"],
            parameters["patch"]
        ).save(parameters["message"])

        await VersionCache(
            parameters["major"],
            parameters["minor"],
            parameters["patch"]
        ).set(parameters["message"])

        return response()
