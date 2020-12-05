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


from sqlalchemy import (
    Table,
    MetaData,
    String,
    Column,
    TIMESTAMP,
    ForeignKey,
    Integer,
    Boolean,
    UniqueConstraint,
    PrimaryKeyConstraint,
    create_engine
)
from datetime import datetime

from sqlalchemy.sql.sqltypes import Float


metadata = MetaData()


update_table = Table(
    "update",
    metadata,
    Column(
        "version",
        String(length=8),
        primary_key=True
    ),
    Column(
        "message",
        String(length=64)
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


user_table = Table(
    "user",
    metadata,
    Column(
        "steam_id",
        String(length=64),
        primary_key=True
    ),
    Column(
        "timestamp",
        TIMESTAMP,
        default=datetime.now
    ),
    Column(
        "name",
        String(length=42)
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


community_type_table = Table(
    "community_type",
    metadata,
    Column(
        "community_type_id",
        Integer,
        primary_key=True
    ),
    Column(
        "community_type",
        String(length=12)
    )
)


community_table = Table(
    "community",
    metadata,
    Column(
        "community_name",
        String(length=32),
        primary_key=True
    ),
    Column(
        "owner_id",
        String(length=64),
        ForeignKey("user.steam_id")
    ),
    Column(
        "community_type_id",
        Integer,
        ForeignKey("community_type.community_type_id"),
        nullable=True
    ),
    Column(
        "timestamp",
        TIMESTAMP,
        default=datetime.now
    ),
    Column(
        "disabled",
        Boolean,
        default=False
    ),
    Column(
        "demos",
        Boolean,
        default=False
    ),
    Column(
        "max_upload",
        Float
    ),
    Column(
        "paid",
        Boolean
    ),
    Column(
        "monthly_cost",
        Float
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


statistic_table = Table(
    "statistic",
    metadata,
    Column(
        "steam_id",
        String(length=64),
        ForeignKey("user.steam_id"),
        primary_key=True
    ),
    Column(
        "community_name",
        String(length=32),
        ForeignKey("community.community_name"),
        primary_key=True
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
    PrimaryKeyConstraint(
        "steam_id",
        "community_name",
        sqlite_on_conflict="REPLACE"
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


api_key_table = Table(
    "api_key",
    metadata,
    Column(
        "api_key",
        String(length=32),
        primary_key=True
    ),
    Column(
        "owner_id",
        String(length=64),
        ForeignKey("user.steam_id")
    ),
    Column(
        "timestamp",
        TIMESTAMP,
        default=datetime.now
    ),
    Column(
        "community_name",
        String(length=32),
        ForeignKey("community.community_name")
    ),
    Column(
        "master",
        Boolean,
        default=False
    ),
    UniqueConstraint(
        "api_key",
        "master"
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
# 3 - Too large

# Team Sides
# 0 - CT
# 1 - T
scoreboard_total_table = Table(
    "scoreboard_total",
    metadata,
    Column(
        "match_id",
        String(length=36),
        primary_key=True
    ),
    Column(
        "community_name",
        String(length=32),
        ForeignKey("community.community_name"),
        primary_key=True
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
    PrimaryKeyConstraint(
        "match_id",
        "community_name"
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


# Team Codes
# 0 = Team 1
# 1 = Team 2
scoreboard_table = Table(
    "scoreboard",
    metadata,
    Column(
        "match_id",
        String(length=36),
        ForeignKey("scoreboard_total.match_id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "steam_id",
        String(length=64),
        ForeignKey("user.steam_id"),
        primary_key=True
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
    PrimaryKeyConstraint(
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
