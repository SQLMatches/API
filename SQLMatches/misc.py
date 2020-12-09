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

from typing import List
from os import path
from secrets import token_urlsafe
from asyncio import sleep
from random import randint

from .tables import community_type_table
from .resources import Sessions, Config


async def cache_community_types(community_types: List[str]):
    """Caches community types.

    Parameters
    ----------
    community_types : List[str]
    """

    query = community_type_table.select(
        community_type_table.c.community_type.in_(community_types)
    ).order_by(community_type_table.c.community_type_id.asc())

    last_id = 0
    async for row in Sessions.database.iterate(query):
        last_id = row["community_type_id"]
        Config.community_types[
            row["community_type"]
        ] = row["community_type_id"]

    for community_type in community_types:
        if community_type not in Config.community_types:
            last_id += 1

            await Sessions.database.execute(
                community_type_table.insert().values(
                    community_type_id=last_id,
                    community_type=community_type
                )
            )

            Config.community_types[community_type] = last_id


class SessionKey:
    def __init__(self, pathway: str = None) -> None:
        self.pathway = path.join(
            path.dirname(path.realpath(__file__)) if not pathway else pathway,
            ".session_key_secret"
        )

    def load(self) -> str:
        try:
            with open(self.pathway, "r") as f:
                return f.read()
        except FileNotFoundError:
            return

    def save(self, key: str = token_urlsafe()) -> str:
        with open(self.pathway, "w") as f:
            f.write(key)

        return key


async def websocket_sleep(min_int: int = 1, max_int: int = 4) -> None:
    """Randomizes websocket timer to help load balance.

    Parameters
    ----------
    min_int : int, optional
        by default 1
    max_int : int, optional
        by default 4
    """

    await sleep(Config.ws_loop_time + randint(min_int, max_int))
