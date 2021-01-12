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


from typing import Any, Dict, List

from datetime import datetime

from sqlalchemy.sql import select, and_, func

from asyncio import sleep

from ..on_conflict import (
    on_scoreboard_conflict,
    on_user_conflict,
    on_statistic_conflict
)
from ..tables import scoreboard_total_table, scoreboard_table, user_table
from ..resources import Sessions

from .models import ScoreboardModel
from ..exceptions import InvalidMatchID


class Match:
    def __init__(self, match_id: str, community_name: str) -> None:
        """Handles interactions with a match

        Paramters
        ---------
        match_id: str
            ID of match
        community_name: str
            Name of community.
        """

        self.match_id = match_id
        self.community_name = community_name

    async def set_demo_status(self, status) -> None:
        """Sets demo status to given value.

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.
        """

        try:
            query = scoreboard_total_table.update().values(
                demo_status=status
            ).where(
                and_(
                    scoreboard_total_table.c.match_id == self.match_id,
                    scoreboard_total_table.c.community_name
                    == self.community_name
                )
            )

            await Sessions.database.execute(query=query)
        except Exception:
            raise InvalidMatchID()

    async def demo_status(self) -> int:
        """
        Gets demo status.

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.

        Returns
        -------
        int
            Status of demo.
        """

        query = select([scoreboard_total_table.c.demo_status]).select_from(
            scoreboard_total_table.join(
                scoreboard_table,
                scoreboard_table.c.match_id ==
                scoreboard_total_table.c.match_id
            )
        ).where(
            and_(
                scoreboard_total_table.c.match_id == self.match_id,
                scoreboard_total_table.c.community_name == self.community_name
            )
        ).distinct()

        demo_status = await Sessions.database.fetch_val(query=query)
        if demo_status is not None:
            return demo_status
        else:
            raise InvalidMatchID()

    async def exists(self) -> bool:
        """Checks if the match exists.

        Returns
        -------
        bool
        """

        query = select([func.count()]).where(
            and_(
                scoreboard_total_table.c.match_id == self.match_id,
                scoreboard_total_table.c.community_name == self.community_name
            )
        )

        return await Sessions.database.fetch_val(query=query) > 0

    async def update(self, team_1_score: int, team_2_score: int,
                     players: List[Dict[str, Dict[str, Any]]] = None,
                     team_1_side: int = None, team_2_side: int = None,
                     end: bool = False) -> None:
        """Updates match details.

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.
        """

        if not await self.exists():
            raise InvalidMatchID()

        team_sides = {}

        if team_1_side is not None:
            team_sides["team_1_side"] = team_1_side

        if team_2_side is not None:
            team_sides["team_2_side"] = team_2_side

        query = scoreboard_total_table.update().values(
            team_1_score=team_1_score,
            team_2_score=team_2_score,
            status=0 if end else 1,
            **team_sides
        ).where(
            and_(
                scoreboard_total_table.c.match_id == self.match_id,
                scoreboard_total_table.c.community_name == self.community_name
            )
        )

        await Sessions.database.execute(query=query)

        if players:
            scoreboard = []
            scoreboard_append = scoreboard.append

            users = []
            users_append = users.append

            statistics = []
            statistics_append = statistics.append

            now = datetime.now()

            for player in players:
                scoreboard_append({
                    "match_id": self.match_id,
                    "steam_id": player["steam_id"],
                    "team": player["team"],
                    "alive": player["alive"],
                    "ping": player["ping"],
                    "kills": player["kills"],
                    "headshots": player["headshots"],
                    "assists": player["assists"],
                    "deaths": player["deaths"],
                    "shots_fired": player["shots_fired"],
                    "shots_hit": player["shots_hit"],
                    "mvps": player["mvps"],
                    "score": player["score"],
                    "disconnected": player["disconnected"]
                })

                users_append({
                    "steam_id": player["steam_id"],
                    "name": player["name"],
                    "timestamp": now
                })

                statistics_append({
                    "community_name": self.community_name,
                    "steam_id": player["steam_id"],
                    "kills": player["kills"],
                    "headshots": player["headshots"],
                    "assists": player["assists"],
                    "deaths": player["deaths"],
                    "shots_fired": player["shots_fired"],
                    "shots_hit": player["shots_hit"],
                    "mvps": player["mvps"]
                })

                await sleep(0.000001)

            await Sessions.database.execute_many(
                query=on_user_conflict(),
                values=users
            )

            await Sessions.database.execute_many(
                query=on_scoreboard_conflict(),
                values=scoreboard
            )

            await Sessions.database.execute_many(
                query=on_statistic_conflict(),
                values=statistics
            )

    async def end(self) -> None:
        """Sets match status to 0

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.
        """

        query = scoreboard_total_table.update().values(
            status=0
        ).where(
            and_(
                scoreboard_total_table.c.match_id == self.match_id,
                scoreboard_total_table.c.community_name == self.community_name
            )
        )

        try:
            await Sessions.database.execute(query=query)
        except Exception:
            raise InvalidMatchID()

    async def scoreboard(self) -> ScoreboardModel:
        """Gets scoreboard data.

        Returns
        ------
        ScoreboardModel
            Holds scoreboard data.
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
            scoreboard_total_table.c.community_name,
            user_table.c.steam_id,
            user_table.c.name,
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
            and_(
                scoreboard_total_table.c.match_id == self.match_id,
                scoreboard_total_table.c.community_name == self.community_name
            )
        )

        scoreboard_data = {
            "match": None,
            "team_1": [],
            "team_2": []
        }

        team_1_append = scoreboard_data["team_1"].append
        team_2_append = scoreboard_data["team_2"].append

        async for row in Sessions.database.iterate(query=query):
            if not scoreboard_data["match"]:
                scoreboard_data["match"] = {
                    "match_id": self.match_id,
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
                    "community_name": row["community_name"]
                }

            team_append = team_1_append if row["team"] == 0 else team_2_append

            team_append({
                "steam_id": row["steam_id"],
                "name": row["name"],
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
            raise InvalidMatchID()
