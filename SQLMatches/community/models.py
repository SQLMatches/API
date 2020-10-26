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

from typing import Generator


class CommunityModel:
    def __init__(self, data) -> None:
        self.master_api_key = data["api_key"]
        self.owner_id = data["owner_id"]
        self.disabled = data["disabled"]
        self.name = data["name"]


class MatchModel:
    def __init__(self, data) -> None:
        self.match_id = data["match_id"]
        self.timestamp = data["timestamp"]
        self.status = data["status"]
        self.demo_status = data["demo_status"]
        self.map = data["map"]
        self.team_1_name = data["team_1_name"]
        self.team_2_name = data["team_2_name"]
        self.team_1_score = data["team_1_score"]
        self.team_2_score = data["team_2_score"]
        self.team_1_side = data["team_1_side"]
        self.team_2_side = data["team_2_side"]


class ScoreboardPlayerModel:
    def __init__(self, data) -> None:
        self.name = data["name"]
        self.steam_id = data["steam_id"]
        self.team = data["team"]
        self.alive = data["alive"]
        self.ping = data["ping"]
        self.kills = data["kills"]
        self.headshots = data["headshots"]
        self.assists = data["assists"]
        self.deaths = data["deaths"]
        self.kdr = round(data["kills"] / data["deaths"], 2) \
            if data["kills"] > 0 and data["deaths"] > 0 else 0.00
        self.hs_percentage = round(
            (data["headshots"] / data["kills"]) * 100, 2) \
            if data["kills"] > 0 and data["headshots"] > 0 else 0.00
        self.hit_percentage = round(
            (data["shots_hit"] / data["shots_fired"]) * 100, 2) \
            if data["shots_fired"] > 0 and data["shots_hit"] > 0 else 0.00
        self.shots_fired = data["shots_fired"]
        self.shots_hit = data["shots_hit"]
        self.mvps = data["mvps"]
        self.score = data["score"]
        self.disconnected = data["disconnected"]


class ScoreboardModel(MatchModel):
    def __init__(self, data) -> None:
        MatchModel.__init__(self, data["match"])

        self.__team_1 = data["team_1"]
        self.__team_2 = data["team_2"]

    def team_1(self) -> Generator[ScoreboardPlayerModel, None, None]:
        """Lists players in team 1.

        Yields
        ------
        ScoreboardPlayerModel
            Holds player data.
        """

        for player in self.__team_1:
            yield ScoreboardPlayerModel(player)

    def team_2(self) -> Generator[ScoreboardPlayerModel, None, None]:
        """Lists players in team 2.

        Yields
        ------
        ScoreboardPlayerModel
            Holds player data.
        """

        for player in self.__team_2:
            yield ScoreboardPlayerModel(player)
