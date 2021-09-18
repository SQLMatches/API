# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

import unittest
from base64 import b64encode

from .shared_vars import DATABASE, ROOT

from .. import SQLMatches, Database


class TestBase(unittest.TestCase):
    sqlmatches: SQLMatches

    headers = {
        "Authorization": "Basic " + b64encode(
            "community:password".encode()
        ).decode()
    }

    def setUp(self) -> None:
        self.sqlmatches = SQLMatches(
            **ROOT,
            database=Database("mysql://{username}:{password}@{server}:{port}/{database}?charset=utf8mb4".format(  # noqa: E501
                **DATABASE
            ))
        )
