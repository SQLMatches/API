from uuid import uuid4
from sqlalchemy import select, func
from typing import Dict, List
from datetime import datetime

from sqlalchemy.sql.elements import ClauseElement

from ...errors import MatchNotFound
from ...tables import (
    scoreboard_total_table, spectator_table,
    scoreboard_table, statistic_table
)
from ...resources import Session

from ...models.match import ScoreboardModel

from .players import MatchPlayers
from .demo import DemoFile


class Match:
    def __init__(self, match_id: str = None) -> None:
        """Interact / create a match.

        Parameters
        ----------
        match_id : str, optional
            If not provided random one will be generated, by default None
        """

        if match_id is None:
            match_id = str(uuid4())

        self.__match_id = match_id

    @property
    def __match_id_query(self) -> ClauseElement:
        return scoreboard_total_table.c.match_id == self.match_id

    @property
    def match_id(self) -> str:
        """The ID of the match.

        Returns
        -------
        str
            ID of match
        """

        return self.__match_id

    @property
    def demo(self) -> DemoFile:
        """Interact with your demo.

        Returns
        -------
        DemoFile
        """

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

    async def spectators(self) -> Dict[str, int]:
        """Return a dictionary of spectator IDs with team.

        Returns
        -------
        Dict[str, int]
            Key is SteamID64, value is team they're spectating.
        """

        query = select([
            spectator_table.c.steam_id, spectator_table.c.team
        ]).select_from(spectator_table).where(
            spectator_table.c.match_id == self.match_id
        )
        spectators = {}
        async for spectator in Session.db.iterate(query):
            spectators[spectator["steam_id"]] = spectator["team"]

        return spectators

    async def exists(self) -> bool:
        """Returns True if the current match exists.

        Returns
        -------
        bool
        """

        return await Session.db.fetch_val(
            select([func.count()]).select_from(
                scoreboard_total_table
            ).where(
                scoreboard_total_table.c.match_id == self.match_id
            )
        ) > 0

    async def scoreboard(self) -> ScoreboardModel:
        """Get the match scoreboard.

        Returns
        -------
        ScoreboardModel

        Raises
        ------
        MatchNotFound
        """

        query = select([
            scoreboard_total_table.c.created,
            scoreboard_total_table.c.status,
            scoreboard_total_table.c.map,
            scoreboard_total_table.c.demo_status,
            scoreboard_total_table.c.team_1_name,
            scoreboard_total_table.c.team_2_name,
            scoreboard_total_table.c.team_1_score,
            scoreboard_total_table.c.team_2_score,
            scoreboard_total_table.c.team_1_side,
            scoreboard_total_table.c.team_2_side,
            statistic_table.c.steam_id,
            statistic_table.c.name,
            statistic_table.c.pfp,
            scoreboard_table.c.team,
            scoreboard_table.c.alive,
            scoreboard_table.c.ping,
            scoreboard_table.c.kills,
            scoreboard_table.c.headshots,
            scoreboard_table.c.assists,
            scoreboard_table.c.deaths,
            scoreboard_table.c.shots_fired,
            scoreboard_table.c.shots_hit,
            scoreboard_table.c.mvps,
            scoreboard_table.c.score,
            scoreboard_table.c.disconnected
        ]).select_from(
            scoreboard_total_table.join(
                scoreboard_table,
                scoreboard_table.c.match_id ==
                scoreboard_total_table.c.match_id
            ).join(
                statistic_table,
                statistic_table.c.steam_id == scoreboard_table.c.steam_id
            )
        ).where(
            scoreboard_total_table.c.match_id == self.match_id
        ).order_by(scoreboard_table.c.score.desc())

        scoreboard_data = {
            "match": None,
            "team_1": [],
            "team_2": []
        }

        team_1_append = scoreboard_data["team_1"].append
        team_2_append = scoreboard_data["team_2"].append

        async for row in Session.db.iterate(query=query):
            if not scoreboard_data["match"]:
                scoreboard_data["match"] = {
                    "match_id": self.match_id,
                    "created": row["created"],
                    "status": row["status"],
                    "demo_status": row["demo_status"],
                    "map_": row["map"],
                    "team_1_name": row["team_1_name"],
                    "team_2_name": row["team_2_name"],
                    "team_1_score": row["team_1_score"],
                    "team_2_score": row["team_2_score"],
                    "team_1_side": row["team_1_side"],
                    "team_2_side": row["team_2_side"]
                }

            team_append = team_1_append if row["team"] == 0 else team_2_append

            team_append({
                "steam_id": row["steam_id"],
                "name": row["name"],
                "pfp": row["pfp"],
                "team": row["team"],
                "alive": row["alive"],
                "ping": row["ping"],
                "kills": row["kills"],
                "headshots": row["headshots"],
                "assists": row["assists"],
                "deaths": row["deaths"],
                "shots_fired": row["shots_fired"],
                "shots_hit": row["shots_hit"],
                "mvps": row["mvps"],
                "score": row["score"],
                "disconnected": row["disconnected"]
            })

        if scoreboard_data["match"]:
            return ScoreboardModel(**scoreboard_data)
        else:
            raise MatchNotFound()

    async def update(self, team_1_name: str = None, map_: str = None,
                     status: int = None, demo_status: int = None,
                     team_2_name: str = None, team_1_score: int = None,
                     team_2_score: int = None, team_1_side: int = None,
                     team_2_side: int = None, pre_setup: bool = None,
                     require_ready: bool = None, connect_wait: int = None
                     ) -> ScoreboardModel:
        """Update / create the match.

        Parameters
        ----------
        team_1_name : str, optional
            by default None
        map_ : str, optional
            by default None
        status : int, optional
            by default None
        demo_status : int, optional
            by default None
        team_2_name : str, optional
            by default None
        team_1_score : int, optional
            by default None
        team_2_score : int, optional
            by default None
        team_1_side : int, optional
            by default None
        team_2_side : int, optional
            by default None
        pre_setup : bool, optional
            by default None
        require_ready : bool, optional
            by default None
        connect_wait : int, optional
            by default None

        Returns
        -------
        ScoreboardModel
        """

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

        return await self.scoreboard()
