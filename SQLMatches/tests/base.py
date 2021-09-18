# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

import asynctest
from starlette.testclient import TestClient

from .shared_vars import DATABASE, ROOT

from .. import SQLMatches, Database


class TestBase(asynctest.TestCase):
    sqlmatches: SQLMatches
    client: TestClient

    headers = {
        "Authorization": "basic community:password"
    }

    def setUp(self) -> None:
        self.sqlmatches = SQLMatches(
            **ROOT,
            database=Database("mysql://{username}:{password}@{server}:{port}/{database}?charset=utf8mb4".format(  # noqa: E501
                **DATABASE
            ))
        )

        self.client = TestClient(self.sqlmatches)
