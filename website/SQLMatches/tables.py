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


from sqlalchemy import Table, MetaData, String, \
    Column, TIMESTAMP, ForeignKey, Integer, Boolean, create_engine


metadata = MetaData()

# Scoreboard total table
# Status codes
# 0 - Finished
# 1 - Live
scoreboard_total = Table(
    "scoreboard_total",
    metadata,
    Column(
        "match_id",
        String(length=36),
        primary_key=True
    ),
    Column(
        "timestamp",
        TIMESTAMP
    ),
    Column(
        "status",
        Integer
    ),
    Column(
        "map",
        String(length=24),
        default=None
    ),
    Column(
        "team_1_name",
        String(length=64)
    ),
    Column(
        "team_2_name",
        String(length=64)
    ),
    Column(
        "team_1_score",
        Integer,
        default=0
    ),
    Column(
        "team_2_score",
        Integer,
        default=0
    ),
    Column(
        "team_1_side",
        Integer,
        default=0
    ),
    Column(
        "team_2_side",
        Integer,
        default=0
    ),
)


# Team Codes
# 0 Teamless
# 1 = CT
# 2 = T
scoreboard = Table(
    "scoreboard",
    metadata,
    Column(
        "match_id",
        String(length=36),
        ForeignKey("scoreboard_total.match_id")
    ),
    Column(
        "steam_id",
        String(length=64)
    ),
    Column(
        "team",
        Integer
    ),
    Column(
        "alive",
        Boolean,
        default=0
    ),
    Column(
        "ping",
        Integer,
        default=0
    ),
    Column(
        "kills",
        Integer,
        default=0
    ),
    Column(
        "headshots",
        Integer,
        default=0
    ),
    Column(
        "assists",
        Integer,
        default=0
    ),
    Column(
        "deaths",
        Integer,
        default=0
    ),
    Column(
        "shots_fired",
        Integer,
        default=0
    ),
    Column(
        "shots_hit",
        Integer,
        default=0
    ),
    Column(
        "mvps",
        Integer,
        default=0
    ),
    Column(
        "score",
        Integer,
        default=0
    ),
    Column(
        "disconnected",
        Boolean,
        default=0
    ),
)


def create_tables(database_url: str) -> None:
    """ Creates tables. """

    metadata.create_all(
        create_engine(database_url)
    )
