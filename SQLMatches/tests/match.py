# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from starlette.testclient import TestClient

from .base import TestBase


class TestMatch(TestBase):
    def test_match_create(self) -> None:
        with TestClient(self.sqlmatches) as client:
            resp = client.post("/api/match/create", json={
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
            }, headers=self.headers)

            self.assertEqual(resp.status_code, 200)
            self.assertIsInstance(resp.json(), dict)

    async def test_create_match_invalid_payload(self) -> None:
        with TestClient(self.sqlmatches) as client:
            resp = client.post("/api/match/create", json={
                "team_1": {
                },
                "team_2": {
                    "name": "2",
                    "side": 0,
                    "score": 0
                },
                "map": "de_mirage",
                "wow": False
            }, headers=self.headers)

            self.assertEqual(resp.status_code, 422)
            self.assertIsInstance(resp.json(), list)
