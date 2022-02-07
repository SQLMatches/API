from typing import TYPE_CHECKING, List
from sqlalchemy import select, and_
from datetime import datetime

from sqlalchemy.sql.elements import ClauseElement

from ...tables import scoreboard_table
from ...resources import Session, Config

from ..sql_on_conflict import on_scoreboard_conflict, on_statistic_conflict


if TYPE_CHECKING:
    from . import Match


class MatchPlayers:
    def __init__(self, upper: "Match", players: List[str]) -> None:
        self.__upper = upper
        self.__players = players

    @property
    def __player_in_match_query(self) -> ClauseElement:
        return and_(
            scoreboard_table.c.match_id == self.__upper.match_id,
            scoreboard_table.c.steam_id.in_(self.__players)
        )

    @property
    def players(self) -> List[str]:
        return self.__players

    async def add_to_match(self, team: int) -> None:
        """Add the players to the match.

        Parameters
        ----------
        team : int
            Team number, normally 1 or 2.
        """

        steam_data = {}
        async with Session.requests.get(
            Config.steam._api_url +
            (f"ISteamUser/GetPlayerSummaries/v2/?key={Config.steam._api_key}"
             f"&steamids={','.join(self.players)}")
        ) as resp:
            if resp.status == 200:
                for user in (await resp.json())["response"]["players"]:
                    steam_data[user["steamid"]] = user

        stats = []
        scoreboard = []

        now = datetime.now()
        for player in self.players:
            stats.append({
                "steam_id": player,
                "name": steam_data[player]["name"][:42]
                if player in steam_data else "Unknown",
                "pfp": steam_data[player]["avatarfull"].replace(
                    "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/",  # noqa: E501
                    ""
                ) if player in steam_data else None,
                "kills": 0,
                "headshots": 0,
                "assists": 0,
                "deaths": 0,
                "shots_fired": 0,
                "shots_hit": 0,
                "mvps": 0,
                "created": now
            })

            scoreboard.append({
                "steam_id": player,
                "match_id": self.__upper.match_id,
                "team": 0,
                "alive": 0,
                "ping": 0,
                "kills": 0,
                "headshots": 0,
                "assists": 0,
                "deaths": 0,
                "shots_fired": 0,
                "shots_hit": 0,
                "mvps": 0,
                "score": 0,
                "disconnected": False
            })

        await Session.db.execute_many(
            on_statistic_conflict(),
            stats
        )

        await Session.db.execute_many(
            on_scoreboard_conflict(),
            scoreboard
        )

    async def remove_from_match(self) -> None:
        """Remove players from match.
        """

        await Session.db.execute(scoreboard_table.delete(
            self.__player_in_match_query
        ))

    async def who_in_match(self) -> List[str]:
        """list of players who have played in match.

        Returns
        -------
        List[str]
        """

        steam_ids = await Session.db.fetch_all(
            select([scoreboard_table.c.steam_id]).select_from(
                scoreboard_table
            ).where(scoreboard_table.c.steam_id.in_(
                self.__player_in_match_query
            ))
        )

        if not steam_ids:
            return []

        return [
            row["steam_id"] for row in steam_ids
        ]
