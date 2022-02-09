from typing import Any, Dict, Generator, List
from datetime import datetime


class _DepthStatsModel:
    def __init__(self, kills: int, deaths: int,
                 headshots: int, shots_hit: int,
                 shots_fired: int) -> None:
        self.kills = kills
        self.deaths = deaths
        self.headshots = headshots
        self.shots_hit = shots_hit
        self.shots_fired = shots_fired

    @property
    def kdr(self) -> float:
        return (
            round(self.kills / self.deaths, 2)
            if self.kills > 0 and self.deaths > 0 else 0.00
        )

    @property
    def hs_percentage(self) -> float:
        return (
            round((self.headshots / self.kills) * 100, 2)
            if self.kills > 0 and self.headshots > 0 else 0.00
        )

    @property
    def hit_percentage(self) -> float:
        return (
            round((self.shots_hit / self.shots_fired) * 100, 2)
            if self.shots_fired > 0 and self.shots_hit > 0 else 0.00
        )


class MatchModel:
    def __init__(self, match_id: str, created: datetime, status: int,
                 demo_status: int, map_: str, team_1_name: str,
                 team_2_name: str, team_1_score: int,
                 team_2_score: int, team_1_side: int,
                 team_2_side: int) -> None:
        self.match_id = match_id
        self.created = created
        self.status = status
        self.demo_status = demo_status
        self.map_ = map_
        self.team_1_name = team_1_name
        self.team_2_name = team_2_name
        self.team_1_score = team_1_score
        self.team_2_score = team_2_score
        self.team_1_side = team_1_side
        self.team_2_side = team_2_side

    @property
    def api_schema(self) -> dict:
        return {
            "match_id": self.match_id,
            "created": self.created.timestamp(),
            "status": self.status,
            "demo_status": self.demo_status,
            "map": self.map_,
            "team_1_name": self.team_1_name,
            "team_2_name": self.team_2_name,
            "team_1_score": self.team_1_score,
            "team_2_score": self.team_2_score,
            "team_1_side": self.team_1_side,
            "team_2_side": self.team_2_side,
        }


class ProfileModel(_DepthStatsModel):
    def __init__(self, name: str, steam_id: str, kills: int, headshots: int,
                 assists: int, deaths: int, pfp: str,
                 shots_fired: int, shots_hit: int,
                 mvps: int, created: datetime, **kwargs) -> None:
        _DepthStatsModel.__init__(
            self, kwargs["kills"], kwargs["deaths"],
            kwargs["headshots"], shots_hit, shots_fired
        )

        self.name = name
        self.steam_id = steam_id
        self.kills = kills
        self.headshots = headshots
        self.assists = assists
        self.deaths = deaths
        self.pfp = pfp
        self.shots_fired = shots_fired
        self.shots_hit = shots_hit
        self.mvps = mvps
        self.created = created

    @property
    def api_schema(self) -> dict:
        return {
            "name": self.name,
            "steam_id": self.steam_id,
            "kills": self.kills,
            "headshots": self.headshots,
            "assists": self.assists,
            "deaths": self.deaths,
            "pfp": self.pfp,
            "kdr": self.kdr,
            "hs_percentage": self.hs_percentage,
            "hit_percentage": self.hit_percentage,
            "shots_fired": self.shots_fired,
            "shots_hit": self.shots_hit,
            "mvps": self.mvps,
            "created": self.created.timestamp()
        }


class _ScoreboardPlayerModel(_DepthStatsModel):
    def __init__(self, name: str, steam_id: str, team: int,
                 alive: bool, ping: int, kills: int, headshots: int,
                 assists: int, deaths: int, shots_fired: int,
                 shots_hit: int, mvps: int, score: int,
                 disconnected: bool, pfp: str) -> None:
        super().__init__(kills, deaths,
                         headshots, shots_hit, shots_fired)

        self.name = name
        self.steam_id = steam_id
        self.team = team
        self.alive = alive
        self.ping = ping
        self.kills = kills
        self.headshots = headshots
        self.assists = assists
        self.deaths = deaths
        self.shots_fired = shots_fired
        self.shots_hit = shots_hit
        self.mvps = mvps
        self.score = score
        self.disconnected = disconnected
        self.pfp = pfp


class ScoreboardModel(MatchModel):
    def __init__(self, team_1: List[Dict[str, Any]],
                 team_2: List[Dict[str, Any]], match: Dict[str, Any]) -> None:
        super().__init__(**match)

        self.__team_1 = team_1
        self.__team_2 = team_2

    def team_1(self) -> Generator[_ScoreboardPlayerModel, None, None]:
        """Lists players in team 1.

        Yields
        ------
        _ScoreboardPlayerModel
            Holds player data.
        """

        for player in self.__team_1:
            yield _ScoreboardPlayerModel(**player)

    def team_2(self) -> Generator[_ScoreboardPlayerModel, None, None]:
        """Lists players in team 2.

        Yields
        ------
        _ScoreboardPlayerModel
            Holds player data.
        """

        for player in self.__team_2:
            yield _ScoreboardPlayerModel(**player)

    @property
    def api_schema(self) -> dict:
        return {
            **super().api_schema,
            "team_1": self.__team_1,
            "team_2": self.__team_2
        }


class ServerModel:
    def __init__(self, ip: str,
                 port: int, name: str, players: int,
                 max_players: int, map_: str) -> None:
        self.ip = ip
        self.port = port
        self.name = name
        self.players = players
        self.max_players = max_players
        self.map_ = map_

    @property
    def api_schema(self) -> dict:
        return {
            "name": self.name,
            "players": self.players,
            "max_players": self.max_players,
            "ip": self.ip,
            "port": self.port,
            "map": self.map_
        }
