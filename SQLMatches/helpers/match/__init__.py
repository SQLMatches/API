from uuid import uuid4
from sqlalchemy import select, func
from typing import List
from datetime import datetime

from sqlalchemy.sql.elements import ClauseElement

from ...tables import scoreboard_total_table
from ...resources import Session

from .players import MatchPlayers
from .demo import DemoFile


class Match:
    def __init__(self, match_id: str = None) -> None:
        """Interact / create a match.

        Parameters
        ----------
        match_id : str, optional
            [description], by default None
        """

        if match_id is None:
            match_id = str(uuid4())

        self.__match_id = match_id

    @property
    def __match_id_query(self) -> ClauseElement:
        return scoreboard_total_table.c.match_id == self.match_id

    @property
    def demo(self) -> DemoFile:
        return DemoFile(self)

    def players(self, players: List[str]) -> MatchPlayers:
        """Interact with players in a match.

        Parameters
        ----------
        players : List[str]
            List of SteamID64s

        Returns
        -------
        MatchPlayers
        """

        return MatchPlayers(self, players)

    async def exists(self) -> bool:
        return await Session.db.fetch_val(
            select([func.count()]).select_from(
                scoreboard_total_table
            ).where(
                scoreboard_total_table.c.match_id == self.match_id
            )
        ) > 0

    async def update(self, team_1_name: str = None, map_: str = None,
                     status: int = None, demo_status: int = None,
                     team_2_name: str = None, team_1_score: int = None,
                     team_2_score: int = None, team_1_side: int = None,
                     team_2_side: int = None, pre_setup: bool = None,
                     require_ready: bool = None, connect_wait: int = None
                     ) -> None:
        values = {}
        if team_1_name is not None:
            values["team_1_name"] = team_1_name
        if team_2_name is not None:
            values["team_2_name"] = team_2_name
        if map_ is not None:
            values["map"] = map_
        if status is not None:
            values["status"] = status
        if demo_status is not None:
            values["demo_status"] = demo_status
        if team_1_score is not None:
            values["team_1_score"] = team_1_score
        if team_2_score is not None:
            values["team_2_score"] = team_2_score
        if team_1_side is not None:
            values["team_1_side"] = team_1_side
        if team_2_side is not None:
            values["team_2_side"] = team_2_side
        if pre_setup is not None:
            values["pre_setup"] = pre_setup
        if require_ready is not None:
            values["require_ready"] = require_ready
        if connect_wait is not None:
            values["connect_wait"] = connect_wait

        if await self.exists():
            scoreboard_total_table.update().where(
                self.__match_id_query
            ).values(**values)
        else:
            values["match_id"] == self.match_id
            values["created"] = datetime.now()
            scoreboard_total_table.insert(
                **values
            )

    @property
    def match_id(self) -> str:
        """The ID of the match.

        Returns
        -------
        str
            ID of match
        """

        return self.__match_id
