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

from itertools import chain

from ..community.models import CommunityModel, MatchModel, ScoreboardModel


def community_to_dict(model: CommunityModel) -> dict:
    return {
        "api_key": model.api_key,
        "owner_id": model.owner_id,
        "disabled": model.disabled
    }


def match_to_dict(model: MatchModel) -> dict:
    return {
        "match_id": model.match_id,
        "timestamp": model.timestamp.strftime("%m/%d/%Y-%H:%M:%S"),
        "status": model.status,
        "demo_status": model.demo_status,
        "map": model.map,
        "team_1_name": model.team_1_name,
        "team_2_name": model.team_2_name,
        "team_1_score": model.team_1_score,
        "team_2_score": model.team_2_score,
        "team_1_side": model.team_1_side,
        "team_2_side": model.team_2_side
    }


def scoreboard_to_dict(model: ScoreboardModel) -> dict:
    scoreboard_data = {
        **match_to_dict(model),
        "team_1": [],
        "team_2": []
    }

    team_1_append = scoreboard_data["team_1"].append
    team_2_append = scoreboard_data["team_2"].append

    for player in chain(model.team_1(), model.team_2()):
        if player.team == 0:
            team_append = team_1_append
        else:
            team_append = team_2_append

        team_append({
            "name": player.name,
            "steam_id": player.steam_id,
            "team": player.team,
            "alive": player.alive,
            "ping": player.ping,
            "kills": player.kills,
            "headshots": player.headshots,
            "assists": player.assists,
            "deaths": player.deaths,
            "kdr": player.kdr,
            "hs_percentage": player.hs_percentage,
            "hit_percentage": player.hit_percentage,
            "shots_fired": player.shots_fired,
            "shots_hit": player.shots_hit,
            "mvps": player.mvps,
            "score": player.score,
            "disconnected": player.disconnected
        })

    return scoreboard_data
