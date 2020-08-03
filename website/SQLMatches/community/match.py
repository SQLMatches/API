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


from sqlalchemy.sql import select, and_

from asyncio import sleep

from ..on_conflict import player_insert_on_conflict_update
from ..tables import scoreboard_total, scoreboard
from ..resources import Sessions

from .models import ScoreboardModel
from .exceptions import InvalidMatchID


class Match:
    def __init__(self, match_id: str, community_name: str) -> None:
        """
        Handles interactions with a match

        Paramters
        ---------
        match_id: str
            ID of match
        community_name: str
            Name of community.
        """

        self.match_id = match_id
        self.community_name = community_name

    async def set_demo_status(self, status):
        """
        Sets demo status to given value.

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.
        """

        try:
            query = scoreboard_total.update().values(
                demo_status=status
            ).where(
                and_(
                    scoreboard_total.c.match_id == self.match_id,
                    scoreboard_total.c.name == self.community_name
                )
            )

            await Sessions.database.execute(query=query)
        except Exception:
            raise InvalidMatchID()

    async def demo_status(self):
        """
        Gets demo status.

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.
        """

        query = select([scoreboard_total.c.demo_status]).select_from(
            scoreboard_total
        ).where(
            and_(
                scoreboard_total.c.match_id == self.match_id,
                scoreboard_total.c.name == self.community_name
            )
        )

        demo_status = await Sessions.database.fetch_val(query=query)
        if demo_status is not None:
            return demo_status
        else:
            raise InvalidMatchID()

    async def exists(self) -> bool:
        """
        Returns a bool depending if the match
        exists or not.
        """

        query = scoreboard_total.count().where(
            and_(
                scoreboard_total.c.match_id == self.match_id,
                scoreboard_total.c.name == self.community_name
            )
        )

        return await Sessions.database.fetch_val(query=query) > 0

    async def update(self, team_1_score: int, team_2_score: int,
                     players: list = None,
                     team_1_side: int = None, team_2_side: int = None,
                     end: bool = False) -> None:
        """
        Updates match details.

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.
        """

        if await self.exists():
            team_sides = {}
            if team_1_side:
                team_sides["team_1_side"] = team_1_side

            if team_2_side:
                team_sides["team_2_side"] = team_2_side

            query = scoreboard_total.update().values(
                team_1_score=team_1_score,
                team_2_score=team_2_score,
                status=0 if end else 1,
                **team_sides
            ).where(
                and_(
                    scoreboard_total.c.match_id == self.match_id,
                    scoreboard_total.c.name == self.community_name
                )
            )

            await Sessions.database.execute(query=query)

            if players:
                query = player_insert_on_conflict_update()

                for player in players:
                    player["match_id"] = self.match_id

                    await sleep(0.0001)

                await Sessions.database.execute_many(
                    query=query,
                    values=players
                )
        else:
            raise InvalidMatchID()

    async def end(self) -> None:
        """
        Sets match status to 0

        Raises
        ------
        InvalidMatchID
            Raised when match ID is invalid.
        """

        if await self.exists():
            query = scoreboard_total.update().values(
                status=0
            ).where(
                and_(
                    scoreboard_total.c.match_id == self.match_id,
                    scoreboard_total.c.name == self.community_name
                )
            )

            await Sessions.database.execute(query=query)
        else:
            raise InvalidMatchID()

    async def scoreboard(self) -> ScoreboardModel:
        """
        Gets scoreboard data.

        Returns
        ------
        ScoreboardModel
            Holds scoreboard data.
        """

        query = select([
            scoreboard_total.c.timestamp,
            scoreboard_total.c.status,
            scoreboard_total.c.map,
            scoreboard_total.c.demo_status,
            scoreboard_total.c.team_1_name,
            scoreboard_total.c.team_2_name,
            scoreboard_total.c.team_1_score,
            scoreboard_total.c.team_2_score,
            scoreboard_total.c.team_1_side,
            scoreboard_total.c.team_2_side,
            scoreboard.c.steam_id,
            scoreboard.c.name,
            scoreboard.c.team,
            scoreboard.c.alive,
            scoreboard.c.ping,
            scoreboard.c.kills,
            scoreboard.c.headshots,
            scoreboard.c.assists,
            scoreboard.c.deaths,
            scoreboard.c.shots_fired,
            scoreboard.c.shots_hit,
            scoreboard.c.mvps,
            scoreboard.c.score,
            scoreboard.c.disconnected
        ]).select_from(
            scoreboard_total.join(
                scoreboard,
                scoreboard.c.match_id == scoreboard_total.c.match_id
            )
        ).where(
            and_(
                scoreboard_total.c.match_id == self.match_id,
                scoreboard_total.c.name == self.community_name
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
                    "team_2_side": row["team_2_side"]
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
            return ScoreboardModel(scoreboard_data)
        else:
            raise InvalidMatchID()
