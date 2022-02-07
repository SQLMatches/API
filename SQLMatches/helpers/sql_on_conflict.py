from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.sql.elements import ClauseElement

from ..tables import scoreboard_table, statistic_table
from ..resources import Session


def on_statistic_conflict() -> ClauseElement:
    """Used for updating a statistics on conflict.
    """

    if Session.db.url.dialect == "mysql":
        query_insert = mysql_insert(statistic_table)
        return query_insert.on_duplicate_key_update(
            name=query_insert.inserted.name,
            kills=statistic_table.c.kills + query_insert.inserted.kills,
            headshots=statistic_table.c.headshots +
            query_insert.inserted.headshots,
            assists=statistic_table.c.assists + query_insert.inserted.assists,
            deaths=statistic_table.c.deaths + query_insert.inserted.deaths,
            shots_fired=statistic_table.c.shots_fired +
            query_insert.inserted.shots_fired,
            shots_hit=statistic_table.c.shots_hit +
            query_insert.inserted.shots_hit,
            mvps=statistic_table.c.mvps + query_insert.inserted.mvps
        )
    elif Session.db.url.dialect == "psycopg2":
        query_insert = postgresql_insert(statistic_table)
        return query_insert.on_conflict_do_update(
            set_=dict(
                name=query_insert.inserted.name,
                kills=statistic_table.c.kills + query_insert.inserted.kills,
                headshots=statistic_table.c.headshots +
                query_insert.inserted.headshots,
                assists=statistic_table.c.assists +
                query_insert.inserted.assists,
                deaths=statistic_table.c.deaths + query_insert.inserted.deaths,
                shots_fired=statistic_table.c.shots_fired +
                query_insert.inserted.shots_fired,
                shots_hit=statistic_table.c.shots_hit +
                query_insert.inserted.shots_hit,
                mvps=statistic_table.c.mvps + query_insert.inserted.mvps
            )
        )
    else:
        return statistic_table.insert  # type: ignore


def on_scoreboard_conflict() -> ClauseElement:
    """Used for updating a player on a scoreboard on conflict.
    """

    if Session.db.url.dialect == "mysql":
        query_insert = mysql_insert(scoreboard_table)
        return query_insert.on_duplicate_key_update(
            team=query_insert.inserted.team,
            alive=query_insert.inserted.alive,
            ping=query_insert.inserted.ping,
            kills=scoreboard_table.c.kills + query_insert.inserted.kills,
            headshots=scoreboard_table.c.headshots +
            query_insert.inserted.headshots,
            assists=scoreboard_table.c.assists + query_insert.inserted.assists,
            deaths=scoreboard_table.c.deaths + query_insert.inserted.deaths,
            shots_fired=scoreboard_table.c.shots_fired +
            query_insert.inserted.shots_fired,
            shots_hit=scoreboard_table.c.shots_hit +
            query_insert.inserted.shots_hit,
            mvps=scoreboard_table.c.mvps + query_insert.inserted.mvps,
            score=scoreboard_table.c.score + query_insert.inserted.score,
            disconnected=query_insert.inserted.disconnected
        )
    elif Session.db.url.dialect == "psycopg2":
        query_insert = postgresql_insert(scoreboard_table)
        return query_insert.on_conflict_do_update(
            set_=dict(
                team=query_insert.inserted.team,
                alive=query_insert.inserted.alive,
                ping=query_insert.inserted.ping,
                kills=scoreboard_table.c.kills + query_insert.inserted.kills,
                headshots=scoreboard_table.c.headshots +
                query_insert.inserted.headshots,
                assists=scoreboard_table.c.assists +
                query_insert.inserted.assists,
                deaths=scoreboard_table.c.deaths +
                query_insert.inserted.deaths,
                shots_fired=scoreboard_table.c.shots_fired +
                query_insert.inserted.shots_fired,
                shots_hit=scoreboard_table.c.shots_hit +
                query_insert.inserted.shots_hit,
                mvps=scoreboard_table.c.mvps + query_insert.inserted.mvps,
                score=scoreboard_table.c.score + query_insert.inserted.score,
                disconnected=query_insert.inserted.disconnected
            )
        )
    else:
        return scoreboard_table.insert  # type: ignore
