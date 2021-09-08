# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from datetime import datetime

from ...resources import Config
from ...enums import MatchStatus, DemoStatus, TeamSides

from .base import ApiSchema


class MatchModel(ApiSchema):
    match_id: str
    team_1_name: str
    team_2_name: str
    team_1_side: TeamSides
    team_2_side: TeamSides
    team_1_score: int
    team_2_score: int
    map_name: str
    timestamp: datetime
    status: MatchStatus
    demo_status: DemoStatus

    def __init__(self, match_id: str, timestamp: datetime, status: int,
                 demo_status: int, map_name: str, team_1_name: str,
                 team_2_name: str, team_1_score: int,
                 team_2_score: int, team_1_side: int,
                 team_2_side: int, **kwargs) -> None:
        self.match_id = match_id
        self.timestamp = timestamp
        self.status = MatchStatus(status)
        self.demo_status = DemoStatus(demo_status)
        self.map_name = map_name
        self.team_1_name = team_1_name
        self.team_2_name = team_2_name
        self.team_1_score = team_1_score
        self.team_2_score = team_2_score
        self.team_1_side = TeamSides(team_1_side)
        self.team_2_side = TeamSides(team_2_side)

        self.cover_image = "{}maps/{}".format(
            Config.backend_url,
            Config.map_images[self.map_name]
            if self.map_name in Config.map_images
            else Config.map_images["invalid"]
        )

    @property
    def api_schema(self) -> dict:
        return {
            "id": self.match_id,
            "timestamp": self.timestamp.timestamp(),
            "map": self.map_name,
            "cover_image": self.cover_image,
            "status": {
                "match": self.status.value,
                "demo": self.demo_status.value,
            },
            "team_1": {
                "name": self.team_1_name,
                "score": self.team_1_score,
                "side": self.team_1_side.value
            },
            "team_2": {
                "name": self.team_2_name,
                "score": self.team_2_score,
                "side": self.team_2_side.value
            }
        }
