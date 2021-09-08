# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from pydantic import BaseModel, Field

from ...constants import TEAM_NAME_LEN
from ...enums import TeamSides


class TeamSpec(BaseModel):
    name: str = Field(min_length=1, max_length=TEAM_NAME_LEN)
    side: TeamSides
    score: int


class MatchCreateSpec(BaseModel):
    team_1: TeamSpec
    team_2: TeamSpec
    map: str
