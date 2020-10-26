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

from sqlalchemy.sql import select, and_, or_

from secrets import token_urlsafe
from datetime import datetime
from uuid import uuid4

from ..resources import Sessions
from ..tables import community, scoreboard_total, scoreboard

from .exceptions import (
    CommunityTaken,
    AlreadyCommunity,
    InvalidCommunity,
    NoOwnership,
    InvalidAPIKey
)
from .models import CommunityModel, MatchModel
from .match import Match


class Community:
    def __init__(self, community_name: str) -> str:
        """Handles community interactions.

        Paramters
        ---------
        community_name: str
            ID of community.
        """

        self.community_name = community_name

    async def create_match(self, team_1_name: str, team_2_name: str,
                           team_1_side: int, team_2_side: int,
                           team_1_score: int, team_2_score: int,
                           map_name: str) -> Match:
        """Creates a match.

        Returns
        -------
        Match
            Used for interacting with matches.
        """

        match_id = str(uuid4())

        query = scoreboard_total.insert().values(
            match_id=match_id,
            team_1_name=team_1_name,
            team_2_name=team_2_name,
            team_1_side=team_1_side,
            team_2_side=team_2_side,
            map=map_name,
            name=self.community_name,
            team_1_score=team_1_score,
            team_2_score=team_2_score,
            status=1,
            demo_status=0,
            timestamp=datetime.now()
        )

        await Sessions.database.execute(query=query)

        return self.match(match_id)

    def match(self, match_id) -> Match:
        """Handles interactions with a match

        Paramters
        ---------
        match_id: str
            ID of match
        """

        return Match(match_id, self.community_name)

    async def regenerate(self) -> None:
        """Regenerates API key.
        """

        query = community.update().values(
            api_key=token_urlsafe(24)
        ).where(community.c.name == self.community_name)

        await Sessions.database.execute(query=query)

    async def exists(self) -> bool:
        """Checks if community exists with name.
        """

        query = community.count().where(
            community.c.name == self.community_name
        )

        return await Sessions.database.fetch_val(query=query) > 0

    async def matches(self, search: str = None,
                      page: int = 1, limit: int = 5
                      ) -> AsyncGenerator[MatchModel, Match]:
        """Lists matches.

        Paramters
        ---------
        search: str
        page: int
        limit: int

        Yields
        ------
        MatchModel
            Holds basic match details.
        Match
            Used for interacting with a match.
        """

        query = select([
            scoreboard_total.c.match_id,
            scoreboard_total.c.timestamp,
            scoreboard_total.c.status,
            scoreboard_total.c.demo_status,
            scoreboard_total.c.map,
            scoreboard_total.c.team_1_name,
            scoreboard_total.c.team_2_name,
            scoreboard_total.c.team_1_score,
            scoreboard_total.c.team_2_score,
            scoreboard_total.c.team_1_side,
            scoreboard_total.c.team_2_side
        ])

        if search:
            like_search = "%{}%".format(search)

            query = query.select_from(
                scoreboard_total.join(
                    scoreboard,
                    scoreboard.c.match_id == scoreboard_total.c.match_id
                )
            ).where(
                and_(
                    scoreboard_total.c.name == self.community_name,
                    or_(
                        scoreboard_total.c.map.like(like_search),
                        scoreboard_total.c.team_1_name.like(like_search),
                        scoreboard_total.c.team_2_name.like(like_search),
                        scoreboard.c.name.like(like_search),
                        scoreboard.c.steam_id == search
                    )
                )
            ).distinct()
        else:
            query = query.select_from(
                scoreboard_total
            ).where(
                scoreboard_total.c.name == self.community_name,
            )

        query = query.order_by(
            scoreboard_total.c.timestamp.desc()
        ).limit(limit).offset((page - 1) * limit if page > 1 else 0)

        async for row in Sessions.database.iterate(query=query):
            yield MatchModel(row), self.match(row["match_id"])

    async def get(self) -> CommunityModel:
        """Gets base community details.

        Returns
        -------
        CommunityModel
            Holds community data.

        Raises
        ------
        InvalidCommunity
            Raised when community ID doesn't exist.
        """

        query = select([
            community.c.api_key,
            community.c.owner_id,
            community.c.disabled
        ]).select_from(
            community
        ).where(
            community.c.name == self.community_name
        )

        row = await Sessions.database.fetch_one(query=query)

        if row:
            return CommunityModel(row)
        else:
            raise InvalidCommunity()

    async def disable(self) -> None:
        """Disables a community.
        """

        query = community.update().where(
            community.c.name == self.community_name
        ).values(disabled=True)

        await Sessions.database.execute(query=query)


async def api_key_to_community(api_key: str) -> Community:
    """Converts API key to community name.

    Raises
    ------
    InvalidAPIKey

    Returns
    -------
    str
        Community name
    """

    query = select([community.c.name]).select_from(
        community
    ).where(
        and_(
            community.c.api_key == api_key,
            community.c.disabled == 0
        )
    )

    row = await Sessions.database.fetch_val(query=query)

    if row:
        return Community(row)
    else:
        raise InvalidAPIKey()


async def get_community_from_owner(steam_id: str) -> Community:
    """Gets community name from owners steamID.

    Raises
    ------
    NoOwnership
        Raised when steam id doesn't own any communties.
    """

    query = select(
        [community.c.name]
    ).select_from(
        community
    ).where(
        and_(
            community.c.owner_id == steam_id,
            community.c.disabled == 0
        )
    )

    name = await Sessions.database.fetch_val(query=query)

    if name:
        return Community(name)
    else:
        raise NoOwnership()


async def owner_exists(steam_id: str) -> bool:
    """Checks if given steam_id owns a community
    """

    query = community.count().where(
        and_(
            community.c.owner_id == steam_id,
            community.c.disabled == 0
        )
    )

    return await Sessions.database.fetch_val(query=query) > 0


async def create_community(steam_id: str, community_name: str,
                           disabled: bool = False
                           ) -> Community:
    """Creates a community.

    Paramters
    ---------
    owner_id: str
        Owner ID.
    name: str
        Name of community.
    disabled: bool
        Defaults to False.

    Returns
    -------
    Community
        Used for interacting with a community

    Raises
    ------
    CommunityTaken
        Raised when community name is taken.
    AlreadyCommunity
        Raised when owner already owns a community.
    """

    if await Community(community_name).exists():
        raise CommunityTaken()

    if await owner_exists(steam_id):
        raise AlreadyCommunity()

    query = community.insert().values(
        name=community_name,
        owner_id=steam_id,
        disabled=disabled,
        api_key=token_urlsafe(24)
    )

    await Sessions.database.execute(query=query)

    return Community(community_name)
