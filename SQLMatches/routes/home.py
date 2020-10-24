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

from ..forms.home import CreatePage

from ..community import get_community_from_owner, create_community
from ..community.exceptions import NoOwnership, CommunityTaken, \
    AlreadyCommunity


class HomePage(HTTPEndpoint):
    async def get(self, request):
        if "steam_id" in request.session:
            try:
                community = await get_community_from_owner(
                    request.session["steam_id"]
                )
            except NoOwnership:
                pass
            else:
                return RedirectResponse(
                    request.url_for(
                        "CommunityPage",
                        community=community.community_name
                    )
                )

        form = await CreatePage.from_formdata(request)

        return TEMPLATE.TemplateResponse("home.html", {
            "request": request,
            "form": form,
        })

    async def post(self, request):
        form = await CreatePage.from_formdata(request)

        if "steam_id" not in request.session or not form.validate_on_submit():
            return RedirectResponse("/?invalid_name=True", status_code=303)

        try:
            community = await create_community(
                steam_id=request.session["steam_id"],
                community_name=form.name.data
            )
        except CommunityTaken:
            return RedirectResponse("/?taken=True", status_code=303)
        except AlreadyCommunity:
            return RedirectResponse("/", status_code=303)
        else:
            return RedirectResponse(
                request.url_for(
                    "CommunityPage",
                    community=community.community_name
                ),
                status_code=303
            )
