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


import asynctest

from .base import TestBase


class TestAPI(TestBase, asynctest.TestCase):
    def test_create_and_update_and_end_match(self) -> None:
        resp = self.client.post(
            "/match/create/",
            json={
                "team_1_name": "Ward",
                "team_2_name": "Doggy",
                "team_1_side": 0,
                "team_2_side": 1,
                "team_1_score": 8,
                "team_2_score": 8,
                "map_name": "de_mirage"
            },
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200, "Match created")

        match_id = (resp.json())["data"]["match_id"]

        resp = self.client.post(
            "/match/{}/".format(match_id),
            json={
                "team_1_score": 15,
                "team_2_score": 8,
                "players": [
                    {
                        "name": "Ward",
                        "steam_id": "76561198077228213",
                        "team": 0,
                        "alive": True,
                        "ping": 69,
                        "kills": 18,
                        "headshots": 8,
                        "assists": 3,
                        "deaths": 10,
                        "shots_fired": 200,
                        "shots_hit": 153,
                        "mvps": 5,
                        "score": 65,
                        "disconnected": False
                    },
                    {
                        "name": "Doggy",
                        "steam_id": "76561198050395665",
                        "team": 0,
                        "alive": True,
                        "ping": 69,
                        "kills": 18,
                        "headshots": 8,
                        "assists": 3,
                        "deaths": 10,
                        "shots_fired": 200,
                        "shots_hit": 153,
                        "mvps": 5,
                        "score": 65,
                        "disconnected": False
                    },
                ]
            },
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200, "Match updated")

        resp = self.client.post(
            "/match/{}/".format(match_id),
            json={
                "team_1_score": 16,
                "team_2_score": 8,
                "players": [
                    {
                        "name": "Weeb",
                        "steam_id": "76561198077228213",
                        "team": 0,
                        "alive": True,
                        "ping": 69,
                        "kills": 18,
                        "headshots": 8,
                        "assists": 3,
                        "deaths": 10,
                        "shots_fired": 200,
                        "shots_hit": 153,
                        "mvps": 5,
                        "score": 65,
                        "disconnected": False
                    },
                    {
                        "name": "Furry",
                        "steam_id": "76561198050395665",
                        "team": 0,
                        "alive": True,
                        "ping": 69,
                        "kills": 18,
                        "headshots": 8,
                        "assists": 3,
                        "deaths": 10,
                        "shots_fired": 200,
                        "shots_hit": 153,
                        "mvps": 5,
                        "score": 65,
                        "disconnected": False
                    },
                ],
                "end": True
            },
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200, "Match ended")

        resp = self.client.get(
            "/match/{}/".format(match_id),
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200, "Get scoreboard ended")

    def test_matches_list(self) -> None:
        resp = self.client.post(
            "/matches/",
            headers=self.basic_auth
        )

        self.assertEqual(resp.status_code, 200, "Match listed")
