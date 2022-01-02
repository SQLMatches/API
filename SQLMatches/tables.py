from sqlalchemy import (
    Table,
    MetaData,
    String,
    Column,
    TIMESTAMP,
    ForeignKey,
    Integer,
    Boolean,
    PrimaryKeyConstraint,
    create_engine
)

metadata = MetaData()

server_table = Table(
    "server",
    metadata,
    Column(
        "ip",
        String(length=15),
        primary_key=True
    ),
    Column(
        "port",
        Integer,
        primary_key=True
    ),
    Column(
        "name",
        String(length=64)
    ),
    Column(
        "players",
        Integer,
        default=0
    ),
    Column(
        "max_players",
        Integer,
        default=0
    ),
    Column(
        "map",
        String(length=24)
    ),
    PrimaryKeyConstraint(
        "ip",
        "port"
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
        primary_key=True
    ),
    Column(
        "name",
        String(length=42)
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

api_key_table = Table(
    "api_key",
    metadata,
    Column(
        "api_key",
        String(length=70),
        primary_key=True
    ),
    Column(
        "steam_id",
        String(length=64),
        ForeignKey("statistic.steam_id")
    ),
    Column(
        "timestamp",
        TIMESTAMP
    ),
    Column(
        "scopes",
        String(length=556)
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
# 3 - Expired

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
        ForeignKey("statistic.steam_id"),
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
    """Create tables in the URL.

    Parameters
    ----------
    url : str
    """

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
