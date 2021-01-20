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

from aiohttp import BasicAuth

from .. import SQLMatches, COMMUNITY_TYPES
from ..settings import (
    DatabaseSettings,
    LocalUploadSettings,
    StripeSettings,
    SmtpSettings
)

from ..community import create_community, Community
from ..exceptions import AlreadyCommunity, CommunityTaken

from starlette.testclient import TestClient


sqlmatches = SQLMatches(
    database_settings=DatabaseSettings(
        username="sqlmatches",
        password="Y2ZRSsje9qZHsxDu",
        server="localhost",
        port=3306,
        database="sqlmatches"
    ),
    stripe_settings=StripeSettings(
        api_key="...",
        testing=True
    ),
    smtp_settings=SmtpSettings(
        hostname="127.0.0.1",
        port=25,
        use_tls=False
    ),
    upload_settings=LocalUploadSettings(),
    friendly_url="http://localhost/api",
    root_steam_id="76561198077228213",
    system_email="noreply@127.0.0.1",
    frontend_url="http://localhost"
)


class TestBase:
    use_default_loop = True

    async def setUp(self) -> None:
        await sqlmatches._startup()

        self.client = TestClient(
            sqlmatches
        )

        STEAM_ID = "76561198077228213"
        COMMUNITY_NAME = "TestLeague"
        EMAIL = "hi@wardpearce.com"

        try:
            community, _ = await create_community(
                community_name=COMMUNITY_NAME,
                steam_id=STEAM_ID,
                community_type=COMMUNITY_TYPES[0],
                email=EMAIL
            )
        except (CommunityTaken, AlreadyCommunity):
            community = await Community(community_name=COMMUNITY_NAME).get()

        self.basic_auth = {
            "Authorization": BasicAuth(
                login="",
                password=community.master_api_key
            ).encode()
        }

    async def tearDown(self) -> None:
        await sqlmatches._shutdown()
