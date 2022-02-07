from uuid import uuid4
from sqlalchemy import select, func
from typing import List

from ...settings import MatchSettings
from ...tables import scoreboard_total_table
from ...resources import Session
from ...errors import MatchIdTaken

from .players import MatchPlayers


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

    async def create(self, match: MatchSettings) -> None:
        if await self.exists():
            raise MatchIdTaken()

    @property
    def match_id(self) -> str:
        """The ID of the match.

        Returns
        -------
        str
            ID of match
        """

        return self.__match_id
