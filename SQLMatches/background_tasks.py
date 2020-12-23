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

from asyncio import sleep
from sqlalchemy.sql import select, and_
from datetime import datetime

from .demos import Demo
from .community.match import Match
from .resources import DemoQueue, Sessions, Config
from .tables import scoreboard_total_table


async def demo_delete() -> None:
    """Handles deleting demos in background off local storage or B2.
    """

    while True:
        for community_matches in list(DemoQueue.matches):
            for match in community_matches["matches"]:
                demo = Demo(Match(
                    match["match_id"],
                    community_matches["community_name"]
                ))

                if demo.delete:
                    await demo.delete()

                await sleep(2.0)

            DemoQueue.matches.remove(match["match_id"])

        await sleep(10.0)


async def match_ender() -> None:
    """If a match doesn't get ended correctly, this will
    close it after X amount of time.
    """

    while True:
        query = select([scoreboard_total_table.c.match_id]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.status == 1,
                scoreboard_total_table.c.timestamp + Config.match_max_length
                <= datetime.now()
            )
        )

        matches_to_end = []
        matches_to_end_append = matches_to_end.append
        async for match in Sessions.database.iterate(query):
            matches_to_end_append({
                "match_id": match["match_id"],
                "status": 0
            })

        await Sessions.database.execute_many(
            scoreboard_total_table.update(),
            matches_to_end
        )

        await sleep(3600.0)


TASKS_TO_SPAWN = [
    demo_delete,
    match_ender
]
