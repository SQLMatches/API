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

from .tables import community_table

from .community import Community
from .community.models import CommunityModel


async def communities(search: str = None, page: int = 1,
                      limit: int = 5, desc: bool = True
                      ) -> AsyncGenerator[CommunityModel, Community]:
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
    CommunityModel
    Community
    """

    query = select([
        community_table.c.community_name,
        community_table.c.owner_id,
        community_table.c.timestamp,
        community_table.c.disabled
    ]).select_from(
        community_table
    ).order_by(
        community_table.c.timestamp.desc() if desc
        else community_table.c.timestamp.asc()
    ).limit(limit).offset((page - 1) * limit if page > 1 else 0)

    if search:
        query = query.where(
            or_(
                community_table.c.community_name.like("%{}%".format(search)),
                community_table.c.owner_id == search
            )
        )

    async for community in Sessions.database.iterate(query=query):
        yield CommunityModel({
            "community_name": community["community_name"],
            "owner_id": community["owner_id"],
            "timestamp": community["timestamp"],
            "disabled": community["disabled"]
        }), Community(community["community_name"])
