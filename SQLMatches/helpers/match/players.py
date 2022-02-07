from typing import TYPE_CHECKING, List
from sqlalchemy import select, and_
from datetime import datetime

from sqlalchemy.sql.elements import ClauseElement

from ...tables import scoreboard_table, spectator_table
from ...resources import Session, Config
from ...errors import MatchNotFound

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

    async def __format_stats(self) -> dict:
        steam_data = {}
        async with Session.requests.get(
            Config.steam._api_url +
            (f"ISteamUser/GetPlayerSummaries/v2/?key={Config.steam._api_key}"
             f"&steamids={','.join(self.players)}")
        ) as resp:
            if resp.status == 200:
                for user in (await resp.json())["response"]["players"]:
                    steam_data[user["steamid"]] = user

        return steam_data

    def __format_player(self, steam_id: str, steam_data: dict,
                        now: datetime) -> dict:
        return {
            "steam_id": steam_id,
            "name": steam_data[steam_id]["name"][:42]
            if steam_id in steam_data else "Unknown",
            "pfp": steam_data[steam_id]["avatarfull"].replace(
                "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/",  # noqa: E501
                ""
            ) if steam_id in steam_data else None,
            "kills": 0,
            "headshots": 0,
            "assists": 0,
            "deaths": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "mvps": 0,
            "created": now
        }

    async def add_as_spectator(self, team: int) -> None:
        """Add a spectator to the game.

        Parameters
        ----------
        team : int
            - 0 = Spec any team
            - 1 = Coach team 1
            - 2 = Coach team 2

        Raises
        ------
        MatchNotFound
        """

        if not await self.__upper.exists():
            raise MatchNotFound()

        steam_data = await self.__format_stats()

        stats = []
        specs = []

        now = datetime.now()
        for player in self.players:
            stats.append(self.__format_player(player, steam_data, now))
            specs.append({
                "match_id": self.__upper.match_id,
                "steam_id": player,
                "team": team
            })

        await Session.db.execute_many(
            on_statistic_conflict(),
            stats
        )
        await Session.db.execute_many(
            spectator_table.insert(),
            specs
        )

    async def add_as_player(self, team: int) -> None:
        """Add the players to the match.

        Parameters
        ----------
        team : int
            Team number

        Raises
        ------
        MatchNotFound
        """

        if not await self.__upper.exists():
            raise MatchNotFound()

        stats = []
        scoreboard = []

        steam_data = await self.__format_stats()

        now = datetime.now()
        for player in self.players:
            stats.append(self.__format_player(player, steam_data, now))

            scoreboard.append({
                "steam_id": player,
                "match_id": self.__upper.match_id,
                "team": team,
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

    async def remove_from_match(self, spectator: bool = False) -> None:
        """Remove players / spectators from match.

        Parameters
        ----------
        spectator : bool, optional
            by default False
        """

        if not spectator:
            await Session.db.execute(scoreboard_table.delete(
                self.__player_in_match_query
            ))
        else:
            await Session.db.execute(spectator_table.delete(and_(
                spectator_table.c.match_id == self.__upper.match_id,
                spectator_table.c.steam_id.in_(self.players)
            )))

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
