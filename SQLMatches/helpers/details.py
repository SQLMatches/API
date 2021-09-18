# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from ..enums import TeamSides


class MatchDetails:
    def __init__(self, map_name: str = None) -> None:
        self.__values = {}

        if map_name is not None:
            self.__values["map_name"] = map_name

    @property
    def values(self) -> dict:
        return self.__values

    def team_1(self, name: str = None, score: int = None,
               side: TeamSides = None) -> "MatchDetails":
        if name is not None:
            self.__values["team_1_name"] = name
        if score is not None:
            self.__values["team_1_score"] = score
        if side is not None:
            self.__values["team_1_side"] = side
        return self

    def team_2(self, name: str = None, score: int = None,
               side: TeamSides = None) -> "MatchDetails":
        if name is not None:
            self.__values["team_2_name"] = name
        if score is not None:
            self.__values["team_2_score"] = score
        if side is not None:
            self.__values["team_2_side"] = side
        return self
