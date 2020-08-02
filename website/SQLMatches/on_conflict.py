from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from .tables import scoreboard
from .resources import Config


def player_insert_on_conflict_update():
    if Config.db_engine == "mysql" or Config.db_engine == "psycopg2":
        if Config.db_engine == "mysql":
            query_insert = mysql_insert(scoreboard)
            query_on_update = query_insert.on_duplicate_key_update(
                name=query_insert.inserted.name,
                team=query_insert.inserted.team,
                alive=query_insert.inserted.alive,
                ping=query_insert.inserted.ping,
                kills=query_insert.inserted.kills,
                headshots=query_insert.inserted.headshots,
                assists=query_insert.inserted.assists,
                deaths=query_insert.inserted.deaths,
                shots_fired=query_insert.inserted.shots_fired,
                shots_hit=query_insert.inserted.shots_hit,
                mvps=query_insert.inserted.mvps,
                score=query_insert.inserted.score,
                disconnected=query_insert.inserted.disconnected
            )
        else:
            query_insert = postgresql_insert(scoreboard)
            query_on_update = query_insert.on_conflict_do_update(
                set_=dict(
                    name=query_insert.inserted.name,
                    team=query_insert.inserted.team,
                    alive=query_insert.inserted.alive,
                    ping=query_insert.inserted.ping,
                    kills=query_insert.inserted.kills,
                    headshots=query_insert.inserted.headshots,
                    assists=query_insert.inserted.assists,
                    deaths=query_insert.inserted.deaths,
                    shots_fired=query_insert.inserted.shots_fired,
                    shots_hit=query_insert.inserted.shots_hit,
                    mvps=query_insert.inserted.mvps,
                    score=query_insert.inserted.score,
                    disconnected=query_insert.inserted.disconnected
                )
            )

        return query_on_update
    else:
        return scoreboard.insert
