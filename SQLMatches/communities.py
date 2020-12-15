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


from typing import AsyncGenerator
from sqlalchemy.sql import select, or_

from .resources import Sessions

from .tables import (
    community_table,
    scoreboard_total_table,
    scoreboard_table,
    user_table
)

from .community import Community
from .community.match import Match
from .community.models import PublicCommunityModel, MatchModel


async def communities(search: str = None, page: int = 1,
                      limit: int = 10, desc: bool = True
                      ) -> AsyncGenerator[PublicCommunityModel, Community]:
    """Used to list communities.

    Parameters
    ----------
    search : str, optional
        by default None
    page : int, optional
        by default 1
    limit : int, optional
        by default 5
    desc : bool, optional
        by default True

    Yields
    ------
    PublicCommunityModel
    Community
    """

    query = select([
        community_table.c.community_name,
        community_table.c.owner_id,
        community_table.c.timestamp,
        community_table.c.disabled
    ]).select_from(
        community_table
    ).where(
        community_table.c.disabled == False  # noqa: E712
    ).order_by(
        community_table.c.timestamp.desc() if desc
        else community_table.c.timestamp.asc()
    ).limit(limit).offset((page - 1) * limit if page > 1 else 0)

    if search:
        query = query.where(
            or_(
                community_table.c.community_name.like("%{}%".format(
                    search.replace(" ", "%")
                )),
                community_table.c.owner_id == search
            )
        )

    async for community in Sessions.database.iterate(query=query):
        yield (
            PublicCommunityModel(**community),
            Community(community["community_name"])
        )


async def matches(search: str = None,
                  page: int = 1, limit: int = 3, desc: bool = True
                  ) -> AsyncGenerator[MatchModel, Match]:
    """Lists matches.

    Paramters
    ---------
    search: str
    page: int
    limit: int
    desc: bool, optional
        by default True

    Yields
    ------
    MatchModel
        Holds basic match details.
    Match
        Used for interacting with a match.
    """

    query = select([
        scoreboard_total_table.c.match_id,
        scoreboard_total_table.c.timestamp,
        scoreboard_total_table.c.status,
        scoreboard_total_table.c.demo_status,
        scoreboard_total_table.c.map,
        scoreboard_total_table.c.team_1_name,
        scoreboard_total_table.c.team_2_name,
        scoreboard_total_table.c.team_1_score,
        scoreboard_total_table.c.team_2_score,
        scoreboard_total_table.c.team_1_side,
        scoreboard_total_table.c.team_2_side,
        scoreboard_total_table.c.community_name
    ])

    if search:
        like_search = "%{}%".format(search)

        query = query.select_from(
            scoreboard_total_table.join(
                scoreboard_table,
                scoreboard_table.c.match_id ==
                scoreboard_total_table.c.match_id
            ).join(
                user_table,
                user_table.c.steam_id == scoreboard_table.c.steam_id
            ).join(
                community_table,
                community_table.c.community_name ==
                scoreboard_total_table.c.community_name
            )
        ).where(
            or_(
                scoreboard_total_table.c.match_id == search,
                scoreboard_total_table.c.map.like(like_search),
                scoreboard_total_table.c.team_1_name.like(like_search),
                scoreboard_total_table.c.team_2_name.like(like_search),
                user_table.c.name.like(like_search),
                user_table.c.steam_id == search
            )
        )
    else:
        query = query.select_from(
            scoreboard_total_table.join(
                scoreboard_table,
                scoreboard_table.c.match_id ==
                scoreboard_total_table.c.match_id
            ).join(
                community_table,
                community_table.c.community_name ==
                scoreboard_total_table.c.community_name
            )
        )

    query = query.where(
        community_table.c.disabled == False  # noqa: E712
    ).distinct().order_by(
        scoreboard_total_table.c.timestamp.desc() if desc
        else scoreboard_total_table.c.timestamp.asc()
    ).limit(limit).offset((page - 1) * limit if page > 1 else 0)

    async for row in Sessions.database.iterate(query=query):
        yield MatchModel(**row), Match(row["match_id"], row["community_name"])
