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

from base64 import b64encode

from .. import SQLMatches
from ..settings import DatabaseSettings, LocalUploadSettings

from ..community import create_community, Community
from ..community.exceptions import CommunityTaken

from starlette.testclient import TestClient


class TestBase:
    async def setUp(self):
        sqlmatches = SQLMatches(
            database_settings=DatabaseSettings(
                username="sqlmatches",
                password="Y2ZRSsje9qZHsxDu",
                server="localhost",
                port=3306,
                database="sqlmatches"
            ),
            upload_settings=LocalUploadSettings(),
            friendly_url="http://127.0.0.1:8000"
        )

        try:
            community, _ = await create_community(
                community_name="TestLeague"
            )
        except CommunityTaken:
            community, _ = Community(community_name="TestLeague").get()

        self.basic_auth = {
            "Authorization": "Basic: {}".format(
                b64encode(community.master_api_key)
            )
        }

        self.client = TestClient(
            sqlmatches
        )