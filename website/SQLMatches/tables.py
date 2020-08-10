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
    Column, TIMESTAMP, ForeignKey, Integer, Boolean, create_engine, \
    UniqueConstraint

from datetime import datetime


metadata = MetaData()


community = Table(
    "community",
    metadata,
    Column(
        "name",
        String(length=32),
        primary_key=True
    ),
    Column(
        "owner_id",
        String(length=64)
    ),
    Column(
        "api_key",
        String(length=32)
    ),
    Column(
        "disabled",
        Boolean,
        default=False
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)

# Scoreboard total table
# Status codes
# 0 - Finished
# 1 - Live

# Demo status codes
# 0 - No demo
# 1 - Processing
# 2 - Ready for Download

# Team Sides
# 0 - CT
# 1 - T
scoreboard_total = Table(
    "scoreboard_total",
    metadata,
    Column(
        "match_id",
        String(length=36),
        primary_key=True
    ),
    Column(
        "name",
        String(length=32),
        ForeignKey("community.name")
    ),
    Column(
        "timestamp",
        TIMESTAMP,
        default=datetime.now
    ),
    Column(
        "status",
        Integer
    ),
    Column(
        "demo_status",
        Integer
    ),
    Column(
        "map",
        String(length=24)
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
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


# Team Codes
# 0 = Team 1
# 1 = Team 2
scoreboard = Table(
    "scoreboard",
    metadata,
    Column(
        "match_id",
        String(length=36),
        ForeignKey("scoreboard_total.match_id"),
        primary_key=True
    ),
    Column(
        "steam_id",
        String(length=64),
        primary_key=True
    ),
    Column(
        "name",
        String(length=42)
    ),
    Column(
        "team",
        Integer
    ),
    Column(
        "alive",
        Boolean,
        default=True
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
        default=False
    ),
    UniqueConstraint(
        "steam_id",
        "match_id",
        sqlite_on_conflict="REPLACE"
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


def create_tables(database_url: str) -> None:
    """ Creates tables. """

    metadata.create_all(
        create_engine(database_url)
    )
