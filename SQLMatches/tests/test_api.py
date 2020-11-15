import asynctest

from .base import TestBase


class TestAPI(TestBase, asynctest.TestCase):
    def test_matches_list(self) -> None:
        resp = self.client.post(
            "/matches",
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200)
