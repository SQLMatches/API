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
from starlette.responses import RedirectResponse
from ..templating import TEMPLATE

from ..community import Community, get_community_name
from ..community.exceptions import InvalidCommunity, NoOwnership

from ..resources import Config


class CommunityPage(HTTPEndpoint):
    async def get(self, request):
        community = Community(request.path_params["community"])

        try:
            base_details = await community.get()
        except InvalidCommunity:
            return RedirectResponse("/")
        else:
            matches = [data async for data, _ in community.matches(
                page=request.path_params["page"] if "page" in
                request.path_params else 1
            )]

            return TEMPLATE.TemplateResponse(
                "community.html",
                {
                    "request": request,
                    "base_details": base_details,
                    "matches": matches,
                    "map_images": Config.map_images
                }
            )

    async def post(self, request):
        if "steam_id" not in request.session:
            return RedirectResponse("/", status_code=303)

        try:
            community_name = await get_community_name(
                request.session["steam_id"]
            )
        except NoOwnership:
            return RedirectResponse("/", status_code=303)
        else:
            await Community(community_name).regenerate()

            return RedirectResponse(
                request.url_for("CommunityPage", community=community_name),
                status_code=303
            )
