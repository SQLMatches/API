# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from typing import List

from .base import DepthStatsModel
from .match import MatchModel

from ...enums import TeamSides


class ScoreboardPlayerModel(DepthStatsModel):
    def __init__(self, name: str, steam_id: str, team: int,
                 alive: bool, ping: int, kills: int, headshots: int,
                 assists: int, deaths: int, shots_fired: int,
                 shots_hit: int, mvps: int, score: int,
                 disconnected: bool, pfp: str, **kwargs) -> None:
        super().__init__(kills, deaths,
                         headshots, shots_hit, shots_fired)

        self.name = name
        self.steam_id = steam_id
        self.pfp = pfp
        self.team = TeamSides(team)
        self.alive = alive
        self.ping = ping
        self.kills = kills
        self.headshots = headshots
        self.assists = assists
        self.deaths = deaths
        self.shots_fired = shots_fired
        self.shots_hit = shots_hit
        self.mvps = mvps
        self.score = score
        self.disconnected = disconnected

    @property
    def api_schema(self) -> dict:
        return {
            "name": self.name,
            "steam_id": self.steam_id,
            "pfp": self.pfp,
            "team": self.team.value,
            "alive": self.alive,
            "ping": self.ping,
            "assists": self.assists,
            "mvps": self.mvps,
            "score": self.score,
            "disconnected": self.disconnected,
            **super().api_schema
        }


class ScoreboardModel(MatchModel):
    def __init__(self, team_1: List[ScoreboardPlayerModel],
                 team_2: List[ScoreboardPlayerModel],
                 **kwargs) -> None:
        super().__init__(**kwargs)

        self.team_1 = team_1
        self.team_2 = team_2

    @property
    def api_schema(self) -> dict:
        schema = super().api_schema
        schema["team_1"]["players"] = [
            player.api_schema for player in self.team_1
        ]
        schema["team_2"]["players"] = [
            player.api_schema for player in self.team_2
        ]
        return schema
