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


from sqlalchemy.sql import select

from ..resources import Sessions
from ..tables import community

from .exceptions import CommunityTaken, AlreadyCommunity, InvalidCommunity, \
    NoOwnership
from .models import CommunityModel

from uuid import uuid4
from secrets import token_urlsafe


class Community:
    def __init__(self, community_name: str) -> str:
        """
        Handles community interactions.

        Paramters
        ---------
        community_name: str
            ID of community.
        """

        self.community_name = community_name

    async def exists(self) -> bool:
        """
        Checks if community exists with name.
        """

        query = community.count().where(
            community.c.name == self.community_name
        )

        return await Sessions.database.fetch_val(query=query) > 0

    async def get(self) -> CommunityModel:
        """
        Gets base community details.

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
        query = community.update().where(
            community.c.name == self.community_name
        ).values(disabled=True)

        await Sessions.database.execute(query=query)


async def get_community_name(steam_id: str) -> str:
    """
    Gets community name from owners steamID.

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
        community.c.owner_id == steam_id
    )

    name = await Sessions.database.fetch_val(query=query)

    if name:
        return name
    else:
        raise NoOwnership()


async def owner_exists(steam_id: str) -> bool:
    """
    Checks if given steam_id owns a community
    """

    query = community.count().where(
        community.c.owner_id == steam_id
    )

    return await Sessions.database.fetch_val(query=query) > 0


async def create_community(steam_id: str, community_name: str,
                           disabled: bool = False) -> (Community, str):
    """
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
    str
        Edit name of community
    """

    community_name = community_name.replace(" ", "-")

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
