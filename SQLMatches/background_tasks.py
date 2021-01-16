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
import logging
from sqlalchemy.sql import select, and_, or_, func, text
from datetime import datetime

from .demos import Demo
from .resources import DemoQueue, Sessions, Config
from .tables import scoreboard_total_table
from .caches import CommunityCache
from .community.match import Match


async def demo_delete() -> None:
    """Handles deleting demos in background off local storage or B2.
    """

    while True:
        for community_name, matches in dict(DemoQueue.matches).items():
            for match_id in matches:
                demo = Demo(Match(
                    match_id,
                    community_name
                ))

                if demo.delete:
                    await demo.delete()
                else:
                    break

                await sleep(5.0)

            DemoQueue.matches.pop(community_name, None)

        await sleep(10.0)


async def expired_demos() -> None:
    """Used to expire demos what are older then the max
    life-span for a demo.
    """

    while True:
        query = select([
            scoreboard_total_table.c.match_id,
            scoreboard_total_table.c.community_name
        ]).select_from(scoreboard_total_table).where(
            and_(
                datetime.now() >= func.timestampadd(
                    text("DAY"),
                    Config.demo_expires.days,
                    scoreboard_total_table.c.timestamp
                ),
                scoreboard_total_table.c.demo_status == 2
            )
        )

        statements = []
        statements_append = statements.append
        async for match in Sessions.database.iterate(query):
            logging.info("Attempting to delete demo of {}".format(
                match["match_id"]
            ))

            if match["community_name"] not in DemoQueue.matches:
                DemoQueue.matches[match["community_name"]] = []

            DemoQueue.matches[match["community_name"]].append(
                match["match_id"]
            )

            statements_append(
                and_(
                    scoreboard_total_table.c.match_id == match["match_id"],
                    scoreboard_total_table.c.community_name ==
                    match["community_name"]
                )
            )

            await (CommunityCache(
                match["community_name"]
            ).scoreboard(match["match_id"])).expire()

        if statements:
            await Sessions.database.execute(
                scoreboard_total_table.update().values(
                    demo_status=4
                ).where(
                    or_(
                        *statements
                    )
                )
            )

        await sleep(43200.0)


async def match_ender() -> None:
    """If a match doesn't get ended correctly, this will
    close it after X amount of time.
    """

    # I'm sorry David, please forgive me. Maybe just turn the big telly on.
    while True:
        query = select([
            scoreboard_total_table.c.match_id,
            scoreboard_total_table.c.community_name
        ]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.status == 1,
                datetime.now() + Config.match_max_length >=
                scoreboard_total_table.c.timestamp
            )
        )

        statements = []
        statements_append = statements.append
        async for match in Sessions.database.iterate(query):
            logging.info("Attempting to end match {}".format(
                match["match_id"]
            ))

            statements_append(
                and_(
                    scoreboard_total_table.c.match_id == match["match_id"],
                    scoreboard_total_table.c.community_name ==
                    match["community_name"]
                )
            )

            await (CommunityCache(
                match["community_name"]
            ).scoreboard(match["match_id"])).expire()

        if statements:
            await Sessions.database.execute(
                scoreboard_total_table.update().values(
                    status=0
                ).where(
                    or_(
                        *statements
                    )
                )
            )

        await sleep(400.0)


TASKS_TO_SPAWN = [
    demo_delete,
    match_ender,
    expired_demos
]
