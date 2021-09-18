# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from datetime import datetime
from typing import List, Tuple
from sqlalchemy import select

from ..resources import Sessions
from ..tables import scoreboard_total_table, scoreboard_table, user_table
from ..enums import MatchStatus, DemoStatus
from ..errors import MatchIdError

from .misc import uuid4
from .details import MatchDetails

from .models.match import MatchModel
from .models.scoreboard import ScoreboardPlayerModel, ScoreboardModel


async def create_match(details: MatchDetails) -> Tuple["MatchModel", "Match"]:
    """Create a new MatchRecord .

    Parameters
    ----------
    details : MatchDetails

    Returns
    -------
    MatchModel
    Match
    """

    values = {
        "match_id": uuid4(),
        "timestamp": datetime.now(),
        "status": MatchStatus.live.value,
        "demo_status": DemoStatus.no_demo.value,
        **details.values
    }

    await Sessions.db.execute(
        scoreboard_total_table.insert().values(**values)
    )

    # TODO: Background task WEBHOOK & WEBSOCKET

    return MatchModel(**values), Match(values["match_id"])


class Match:
    def __init__(self, match_id: str) -> None:
        """Initialize match .

        Parameters
        ----------
        match_id : str
        """
        self._match_id = match_id

    async def update(self, details: MatchDetails) -> None:
        pass

    async def get(self) -> ScoreboardModel:
        """Get the current scoreboard.

        Returns
        -------
        ScoreboardModel

        Raises
        ------
        MatchIdError
        """

        query = select([
            scoreboard_total_table.c.timestamp,
            scoreboard_total_table.c.status,
            scoreboard_total_table.c.map,
            scoreboard_total_table.c.demo_status,
            scoreboard_total_table.c.team_1_name,
            scoreboard_total_table.c.team_2_name,
            scoreboard_total_table.c.team_1_score,
            scoreboard_total_table.c.team_2_score,
            scoreboard_total_table.c.team_1_side,
            scoreboard_total_table.c.team_2_side,
            user_table.c.steam_id,
            user_table.c.name,
            user_table.c.pfp,
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
                user_table,
                user_table.c.steam_id == scoreboard_table.c.steam_id
            )
        ).where(
            scoreboard_total_table.c.match_id == self._match_id
        ).order_by(scoreboard_table.c.score.desc())

        match = {}
        team_1: List[ScoreboardPlayerModel] = []
        team_2: List[ScoreboardPlayerModel] = []

        async for row in Sessions.db.iterate(query=query):
            if not match:
                match = {
                    "match_id": self._match_id,
                    "timestamp": row["timestamp"],
                    "status": row["status"],
                    "demo_status": row["demo_status"],
                    "map": row["map"],
                    "team_1_name": row["team_1_name"],
                    "team_2_name": row["team_2_name"],
                    "team_1_score": row["team_1_score"],
                    "team_2_score": row["team_2_score"],
                    "team_1_side": row["team_1_side"],
                    "team_2_side": row["team_2_side"],
                }

            team_append = team_1.append if row["team"] == 0 else team_2.append

            team_append(ScoreboardPlayerModel(
                steam_id=row["steam_id"],
                name=row["name"],
                team=row["team"],
                alive=row["alive"],
                ping=row["ping"],
                kills=row["kills"],
                headshots=row["headshots"],
                assists=row["assists"],
                deaths=row["deaths"],
                shots_fired=row["shots_fired"],
                shots_hit=row["shots_hit"],
                mvps=row["mvps"],
                score=row["score"],
                disconnected=row["disconnected"],
                pfp=row["pfp"]
            ))

        if match:
            return ScoreboardModel(
                team_1=team_1,
                team_2=team_2,
                **match
            )
        else:
            raise MatchIdError()
