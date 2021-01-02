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


from operator import or_
from typing import Tuple
from sqlalchemy.sql import select, and_, func
from secrets import token_urlsafe
from datetime import datetime

from ..resources import Sessions, Config

from ..tables import (
    community_table,
    api_key_table,
)

from ..decorators import (
    validate_community_type,
    validate_webhooks,
    validate_community_name,
    validate_email
)

from ..user import create_user

from ..exceptions import (
    CommunityTaken,
    AlreadyCommunity,
    NoOwnership,
    InvalidAPIKey,
    UserExists
)
from .models import (
    CommunityModel
)

from .community import Community


async def api_key_to_community(api_key: str) -> Tuple[Community, bool]:
    """Converts API key to community name.

    Raises
    ------
    InvalidAPIKey

    Returns
    -------
    str
        Community name
    bool
        If key is a master key.
    """

    query = select([
        community_table.c.community_name, api_key_table.c.master
    ]).select_from(
        community_table.join(
            api_key_table,
            api_key_table.c.community_name == community_table.c.community_name
        )
    ).where(
        and_(
            api_key_table.c.api_key == api_key,
            community_table.c.disabled == False,  # noqa: E712
        )
    ).where(
        or_(
            api_key_table.c.master == True,  # noqa: E712
            community_table.c.allow_api_access == True,  # noqa: E712
        )
    )

    row = await Sessions.database.fetch_one(query=query)

    if row:
        return Community(row["community_name"]), bool(row["master"])
    else:
        raise InvalidAPIKey()


async def get_community_from_owner(steam_id: str) -> Community:
    """Gets community name from owners steamID.

    Raises
    ------
    NoOwnership
        Raised when steam id doesn't own any communties.
    """

    query = select([
        community_table.c.community_name
    ]).select_from(
        community_table
    ).where(
        and_(
            community_table.c.owner_id == steam_id,
            community_table.c.disabled == 0
        )
    )

    community_name = await Sessions.database.fetch_val(query=query)

    if community_name:
        return Community(community_name)
    else:
        raise NoOwnership()


async def owner_exists(steam_id: str) -> bool:
    """Checks if given steam_id owns a community
    """

    query = select([func.count()]).select_from(community_table).where(
        and_(
            community_table.c.owner_id == steam_id,
            community_table.c.disabled == 0
        )
    )

    return await Sessions.database.fetch_val(query=query) > 0


@validate_webhooks
@validate_community_name
@validate_community_type
@validate_email
async def create_community(steam_id: str, community_name: str, email: str,
                           disabled: bool = False, demos: bool = True,
                           community_type: str = None,
                           allow_api_access: bool = False,
                           match_start_webhook: str = None,
                           round_end_webhook: str = None,
                           match_end_webhook: str = None
                           ) -> Tuple[CommunityModel, Community]:
    """[summary]

    Parameters
    ----------
    steam_id : str
    community_name : str
    email : str
    disabled : bool, optional
        by default False
    demos : bool, optional
        by default True
    community_type : str, optional
        by default None
    allow_api_access : bool, optional
        by default False
    match_start_webhook : str, optional
        by default None
    round_end_webhook : str, optional
        by default None
    match_end_webhook : str, optional
        by default None

    Returns
    -------
    CommunityModel
    Community
        Used for interacting with a community

    Raises
    ------
    CommunityTaken
        Raised when community name is taken.
    AlreadyCommunity
        Raised when owner already owns a community.
    InvalidCommunityName
        Raised when community name isn't alphanumeric
        or character length is above 32 or below 4.
    InvalidCommunityType
        Raised when community type isn't valid.
    InvalidUploadSize
        Raised when upload size is incorrect.
    """

    if community_type:
        community_type_id = Config.community_types[community_type]
    else:
        community_type_id = None

    if await owner_exists(steam_id):
        raise AlreadyCommunity()

    try:
        await create_user(steam_id, "Unknown")
    except UserExists:
        pass

    customer, _ = await Sessions.stripe.create_customer(
        name=community_name
    )

    now = datetime.now()

    query = community_table.insert().values(
        community_name=community_name,
        owner_id=steam_id,
        disabled=disabled,
        demos=demos,
        timestamp=now,
        community_type_id=community_type_id,
        allow_api_access=allow_api_access,
        match_start_webhook=match_start_webhook,
        round_end_webhook=round_end_webhook,
        match_end_webhook=match_end_webhook,
        customer_id=customer.id,
        email=email
    )

    try:
        await Sessions.database.execute(query=query)
    except Exception:
        raise CommunityTaken()
    else:
        api_key = token_urlsafe(24)

        query = api_key_table.insert().values(
            api_key=api_key,
            owner_id=steam_id,
            timestamp=now,
            community_name=community_name,
            master=True
        )

        await Sessions.database.execute(query=query)

        return CommunityModel(
            api_key=api_key,
            owner_id=steam_id,
            disabled=disabled,
            community_name=community_name,
            timestamp=now,
            allow_api_access=allow_api_access,
            match_start_webhook=match_start_webhook,
            match_end_webhook=match_end_webhook,
            round_end_webhook=round_end_webhook,
            email=email
        ), Community(community_name)
