# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from .base import TestBase


class TestMatch(TestBase):
    def test_match_create(self) -> None:
        resp = self.client.get("/api/match/create", json={
            "team_1": {
                "name": "1",
                "side": 0,
                "score": 0
            },
            "team_2": {
                "name": "2",
                "side": 0,
                "score": 0
            },
            "map": "de_mirage"
        })

        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), dict)

    def test_create_match_invalid_payload(self) -> None:
        resp = self.client.get("/api/match/create", json={
            "team_1": {
            },
            "team_2": {
                "name": "2",
                "side": 0,
                "score": 0
            },
            "map": "de_mirage",
            "wow": False
        })

        print(resp.status_code)
        print(resp.json())
