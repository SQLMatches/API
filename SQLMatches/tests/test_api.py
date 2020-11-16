import re
import asynctest

from .base import TestBase


class TestAPI(TestBase, asynctest.TestCase):
    def test_create_match(self) -> None:
        resp = self.client.post(
            "/match/create/",
            json={
                "team_1_name": "Ward",
                "team_2_name": "Doggy",
                "team_1_side": 0,
                "team_2_side": 1,
                "team_1_score": 16,
                "team_2_score": 8,
                "map_name": "de_mirage"
            },
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200)

    def test_matches_list(self) -> None:
        resp = self.client.post(
            "/matches/",
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200)
