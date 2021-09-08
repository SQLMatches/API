# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""


from sqlalchemy import (
    String,
    Integer,
    Boolean,
    PrimaryKeyConstraint,
    ForeignKey,
    Table,
    MetaData,
    Column,
    TIMESTAMP,
    create_engine
)

from .constants import (
    TEAM_NAME_LEN, MAP_LEN, MATCH_ID_LEN, STEAM_ID_LEN,
    NAME_LEN, PFP_LEN, FILE_ID_LEN
)


metadata = MetaData()


# User table
user_table = Table(
    "user",
    metadata,
    Column(
        "name",
        String(length=NAME_LEN)
    ),
    Column(
        "steam_id",
        String(length=STEAM_ID_LEN),
        primary_key=True
    ),
    Column(
        "pfp",
        String(length=PFP_LEN)
    ),
    Column(
        "timestamp",
        TIMESTAMP
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
# 4 - Expired

# Team Sides
# 0 - CT
# 1 - T
scoreboard_total_table = Table(
    "scoreboard_total",
    metadata,
    Column(
        "match_id",
        String(length=MATCH_ID_LEN),
        primary_key=True
    ),
    Column(
        "file_id",
        String(length=FILE_ID_LEN),
        nullable=True
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
        "demo_status",
        Integer
    ),
    Column(
        "map_name",
        String(length=MAP_LEN)
    ),
    Column(
        "team_1_name",
        String(length=TEAM_NAME_LEN)
    ),
    Column(
        "team_2_name",
        String(length=TEAM_NAME_LEN)
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
scoreboard_table = Table(
    "scoreboard",
    metadata,
    Column(
        "match_id",
        String(length=MATCH_ID_LEN),
        ForeignKey("scoreboard_total.match_id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "steam_id",
        String(length=TEAM_NAME_LEN),
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


def create_tables(url: str) -> None:
    """Creates tables.
    """

    # Converts to sql engine for sqlalchemy
    if "mysql" in url:
        old_engine = "mysql"
        engine = "pymysql"
    elif "sqlite" in url:
        old_engine = "sqlite"
        engine = "sqlite3"
    elif "postgresql" in url:
        old_engine = "postgresql"
        engine = "psycopg2"
    else:
        assert False, "Invalid database URL engine."

    metadata.create_all(
        create_engine(url.replace(old_engine, f"{old_engine}+{engine}"))
    )
