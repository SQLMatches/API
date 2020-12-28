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

from typing import Any, Dict, Generator, List
from datetime import datetime

from ..resources import Config


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


class PublicCommunityModel:
    def __init__(self, owner_id: str, disabled: bool, community_name: str,
                 timestamp: datetime) -> None:
        self.owner_id = owner_id
        self.disabled = disabled
        self.community_name = community_name
        self.timestamp = timestamp

    @property
    def public_community_api_schema(self) -> dict:
        return {
            "community_name": self.community_name,
            "owner_id": self.owner_id,
            "disabled": self.disabled,
            "timestamp": self.timestamp.strftime(Config.timestamp_format),
        }


class CommunityModel(PublicCommunityModel):
    def __init__(self, allow_api_access: bool,
                 api_key: str,
                 match_start_webhook: str,
                 round_end_webhook: str,
                 match_end_webhook: str,
                 max_upload: float = None,
                 amount: float = None,
                 customer_id: str = None,
                 **kwargs) -> None:
        super().__init__(**kwargs)

        self.master_api_key = api_key
        self.max_upload = (Config.free_upload_size if not
                           max_upload else max_upload)
        self.amount = amount if amount else 0.0
        self.allow_api_access = allow_api_access
        self.match_start_webhook = match_start_webhook
        self.round_end_webhook = round_end_webhook
        self.match_end_webhook = match_end_webhook
        self.customer_id = customer_id

    @property
    def community_api_schema(self) -> dict:
        return {
            "community_name": self.community_name,
            "master_api_key": self.master_api_key,
            "owner_id": self.owner_id,
            "disabled": self.disabled,
            "timestamp": self.timestamp.strftime(Config.timestamp_format),
            "max_upload": self.max_upload,
            "amount": self.amount,
            "allow_api_access": self.allow_api_access,
            "match_start_webhook": self.match_start_webhook,
            "round_end_webhook": self.round_end_webhook,
            "match_end_webhook": self.match_end_webhook,
            "customer_id": self.customer_id
        }


class MatchModel:
    def __init__(self, match_id: str, timestamp: datetime, status: int,
                 demo_status: int, map: str, team_1_name: str,
                 team_2_name: str, team_1_score: int,
                 team_2_score: int, team_1_side: int,
                 team_2_side: int, community_name: str) -> None:
        self.match_id = match_id
        self.timestamp = timestamp
        self.status = status
        self.demo_status = demo_status
        self.map = map
        self.team_1_name = team_1_name
        self.team_2_name = team_2_name
        self.team_1_score = team_1_score
        self.team_2_score = team_2_score
        self.team_1_side = team_1_side
        self.team_2_side = team_2_side
        self.cover_image = "{}maps/{}".format(
            Config.url,
            Config.map_images[self.map] if self.map in Config.map_images
            else "invalid.png"
        )
        self.community_name = community_name

    @property
    def match_api_schema(self) -> dict:
        return {
            "match_id": self.match_id,
            "timestamp": self.timestamp.strftime(Config.timestamp_format),
            "status": self.status,
            "demo_status": self.demo_status,
            "map": self.map,
            "team_1_name": self.team_1_name,
            "team_2_name": self.team_2_name,
            "team_1_score": self.team_1_score,
            "team_2_score": self.team_2_score,
            "team_1_side": self.team_1_side,
            "team_2_side": self.team_2_side,
            "cover_image": self.cover_image,
            "community_name": self.community_name
        }


class PaymentModel:
    def __init__(self, payment_id: str, amount: float,
                 timestamp: datetime.now, subscription_id: str,
                 max_upload: float, expires: datetime.now) -> None:
        self.payment_id = payment_id
        self.amount = amount
        self.timestamp = timestamp
        self.subscription_id = subscription_id
        self.max_upload = max_upload
        self.expires = expires

    @property
    def payment_api_schema(self) -> dict:
        return {
            "payment_id": self.payment_id,
            "amount": self.amount,
            "timestamp": self.timestamp.strftime(Config.timestamp_format),
            "max_upload": self.max_upload,
            "expires": self.expires.strftime(Config.timestamp_format),
            "subscription_id": self.subscription_id
        }


class ProfileModel(_DepthStatsModel):
    def __init__(self, name: str, steam_id: str, kills: int, headshots: int,
                 assists: int, deaths: int, shots_fired: int, shots_hit: int,
                 mvps: int, timestamp: datetime) -> None:
        _DepthStatsModel.__init__(self, kills, deaths,
                                  headshots, shots_hit, shots_fired)

        self.name = name
        self.steam_id = steam_id
        self.kills = kills
        self.headshots = headshots
        self.assists = assists
        self.deaths = deaths
        self.shots_fired = shots_fired
        self.shots_hit = shots_hit
        self.mvps = mvps
        self.timestamp = timestamp

    @property
    def profile_api_schema(self) -> dict:
        return {
            "name": self.name,
            "steam_id": self.steam_id,
            "kills": self.kills,
            "headshots": self.headshots,
            "assists": self.assists,
            "deaths": self.deaths,
            "kdr": self.kdr,
            "hs_percentage": self.hs_percentage,
            "hit_percentage": self.hit_percentage,
            "shots_fired": self.shots_fired,
            "shots_hit": self.shots_hit,
            "mvps": self.mvps,
            "timestamp": self.timestamp.strftime(Config.timestamp_format)
        }


class _ScoreboardPlayerModel(_DepthStatsModel):
    def __init__(self, name: str, steam_id: str, team: int,
                 alive: bool, ping: int, kills: int, headshots: int,
                 assists: int, deaths: int, shots_fired: int,
                 shots_hit: int, mvps: int, score: int,
                 disconnected: bool) -> None:
        _DepthStatsModel.__init__(self, kills, deaths,
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


class ScoreboardModel(MatchModel):
    def __init__(self, team_1: List[Dict[str, Any]],
                 team_2: List[Dict[str, Any]], match: Dict[str, Any]) -> None:
        MatchModel.__init__(self, **match)

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
    def scoreboard_api_schema(self) -> dict:
        return {
            **self.match_api_schema,
            "team_1": self.__team_1,
            "team_2": self.__team_2
        }


class CommunityStatsModel:
    def __init__(self, total_matches: int, active_matches: int,
                 stored_demos: int, total_users: int) -> None:
        self.total_matches = total_matches
        self.active_matches = active_matches
        self.stored_demos = stored_demos
        self.total_users = total_users

    @property
    def stats_api_schema(self) -> dict:
        return {
            "total_matches": self.total_matches,
            "active_matches": self.active_matches,
            "stored_demos": self.stored_demos,
            "total_users": self.total_users
        }
