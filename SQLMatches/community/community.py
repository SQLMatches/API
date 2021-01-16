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


from typing import AsyncGenerator, List, Tuple
from uuid import uuid4
from datetime import datetime
from secrets import token_urlsafe
from email.mime.text import MIMEText

from sqlalchemy.sql import select, and_, or_, func

from ..resources import Sessions, Config, DemoQueue

from ..decorators import (
    validate_community_type,
    validate_webhooks,
    validate_email
)


from ..templates import render_html

from ..tables import (
    community_table,
    scoreboard_total_table,
    scoreboard_table,
    user_table,
    api_key_table,
    statistic_table,
    payment_table
)

from ..exceptions import (
    InvalidCommunity,
    InvalidSteamID,
    NoActivePayment
)

from .models import (
    CommunityModel,
    MatchModel,
    ProfileModel,
    CommunityStatsModel,
    PublicCommunityModel
)

from .match import Match
from .payment import CommunityPayment


class Community(CommunityPayment):
    def __init__(self, community_name: str) -> str:
        """Handles community interactions.

        Paramters
        ---------
        community_name: str
            ID of community.
        """

        self.community_name = community_name

    async def email(self, title: str, content: str,
                    link_href: str, link_text: str) -> None:
        """Used to send email to community owner.

        Parameters
        ----------
        title : str
        content : str
        link_href : str
        link_text : str
        """

        community = await self.get()

        message = MIMEText(render_html(
            "email.html",
            {
                "title": title,
                "content": content,
                "link": {
                    "href": link_href,
                    "text": link_text
                }
            }
        ), "html", "utf-8")

        message["From"] = Config.system_email
        message["To"] = community.email
        message["Subject"] = "{} - {}".format(
            title,
            (datetime.now()).strftime(Config.timestamp_format)
        )

        await Sessions.smtp.send_message(message)

    @validate_webhooks
    @validate_community_type
    @validate_email
    async def update(self, demos: bool = None,
                     community_type: str = None,
                     match_start_webhook: str = None,
                     round_end_webhook: str = None,
                     match_end_webhook: str = None,
                     allow_api_access: bool = None,
                     email: str = None) -> CommunityModel:
        """Used to update a community.

        Parameters
        ----------
        demos : bool, optional
            by default None
        community_type : str, optional
            by default None
        match_start_webhook : str, optional
            by default None
        round_end_webhook : str, optional
            by default None
        match_end_webhook : str, optional
            by default None
        allow_api_access : bool, optional
            by default None
        email : str, optional
            by default None

        Returns
        -------
        CommunityModel
        """

        values = {}

        if community_type is not None:
            values["community_type_id"] = Config.community_types[
                community_type
            ]

        if demos is not None:
            values["demos"] = demos

        if allow_api_access is not None:
            values["allow_api_access"] = allow_api_access

        if match_start_webhook:
            values["match_start_webhook"] = match_start_webhook

        if round_end_webhook:
            values["round_end_webhook"] = round_end_webhook

        if match_end_webhook:
            values["match_end_webhook"] = match_end_webhook

        if email:
            values["email"] = email

        if values:
            query = community_table.update().values(
                **values
            ).where(
                community_table.c.community_name == self.community_name
            )

            await Sessions.database.execute(query)

        return await self.get()

    async def stats(self) -> CommunityStatsModel:
        """Gets basic stats about community.

        Returns
        -------
        CommunityStatsModel
        """

        sub_active_matches = select([
            func.count().label("active_matches")
        ]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.community_name == self.community_name,
                scoreboard_total_table.c.status == 1
            )
        ).alias("sub_active_matches")

        sub_stored_demos = select([
            func.count().label("stored_demos")
        ]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.community_name == self.community_name,
                scoreboard_total_table.c.demo_status == 2
            )
        ).alias("sub_stored_demos")

        sub_total_matches = select([
            func.count().label("total_matches"),
        ]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.community_name == self.community_name,
                scoreboard_total_table.c.status == 0
            )
        ).alias("sub_total_matches")

        sub_total_users = select([
            func.count().label("total_users"),
        ]).select_from(
            statistic_table
        ).where(
            statistic_table.c.community_name == self.community_name
        ).alias("sub_total_users")

        query = select([
            sub_total_users.c.total_users,
            sub_active_matches.c.active_matches,
            sub_stored_demos.c.stored_demos,
            sub_total_matches.c.total_matches
        ])

        return CommunityStatsModel(
            **await Sessions.database.fetch_one(query)
        )

    async def profile(self, steam_id: str) -> ProfileModel:
        """Get user profile.

        Parameters
        ----------
        steam_id : str

        Returns
        -------
        ProfileModel

        Raises
        ------
        InvalidSteamID
        """

        query = select([
            user_table.c.name,
            user_table.c.timestamp,
            statistic_table.c.steam_id,
            statistic_table.c.kills,
            statistic_table.c.headshots,
            statistic_table.c.assists,
            statistic_table.c.deaths,
            statistic_table.c.shots_fired,
            statistic_table.c.shots_hit,
            statistic_table.c.mvps
        ]).select_from(
            statistic_table.join(
                user_table,
                user_table.c.steam_id == statistic_table.c.steam_id
            )
        ).where(
            and_(
                statistic_table.c.steam_id == steam_id,
                statistic_table.c.community_name == self.community_name
            )
        )

        row = await Sessions.database.fetch_one(query=query)
        if row:
            return ProfileModel(**row)
        else:
            raise InvalidSteamID()

    async def delete_matches(self, matches: List[str]) -> None:
        """Used to bulk delete matches.

        Parameters
        ----------
        matches : List[str]
            List of match IDs to delete.
        """

        await Sessions.database.execute(
            scoreboard_total_table.delete().where(
                scoreboard_total_table.c.match_id ==
                scoreboard_table.c.match_id
            ).where(
                and_(
                    scoreboard_total_table.c.community_name ==
                    self.community_name,
                    scoreboard_total_table.c.match_id.in_(matches)
                )
            )
        )

        # Todo
        # Work out sqlalchemy left joining delete,
        # so i don't need this ugly mess.
        await Sessions.database.execute(
            scoreboard_total_table.delete().where(
                and_(
                    scoreboard_total_table.c.community_name
                    == self.community_name,
                    scoreboard_total_table.c.match_id.in_(matches)
                )
            )
        )

        if Config.upload_type:
            if self.community_name not in DemoQueue.matches:
                DemoQueue.matches[self.community_name] = matches
            else:
                DemoQueue.matches[self.community_name] += matches

    async def create_match(self, team_1_name: str, team_2_name: str,
                           team_1_side: int, team_2_side: int,
                           team_1_score: int, team_2_score: int,
                           map_name: str) -> Tuple[MatchModel, Match]:
        """Creates a match.

        Returns
        -------
        Match
            Used for interacting with matches.
        """

        match_id = str(uuid4())
        now = datetime.now()
        status = 1
        demo_status = 0

        query = scoreboard_total_table.insert().values(
            match_id=match_id,
            team_1_name=team_1_name,
            team_2_name=team_2_name,
            team_1_side=team_1_side,
            team_2_side=team_2_side,
            map=map_name,
            community_name=self.community_name,
            team_1_score=team_1_score,
            team_2_score=team_2_score,
            status=status,
            demo_status=demo_status,
            timestamp=now
        )

        await Sessions.database.execute(query=query)

        return MatchModel(
            match_id=match_id, timestamp=now, status=status,
            demo_status=demo_status, map=map_name, team_1_name=team_1_name,
            team_2_name=team_2_name, team_1_score=team_1_score,
            team_2_score=team_2_score, team_1_side=team_1_side,
            team_2_side=team_2_side, community_name=self.community_name
        ), self.match(match_id)

    def match(self, match_id) -> Match:
        """Handles interactions with a match

        Paramters
        ---------
        match_id: str
            ID of match
        """

        return Match(match_id, self.community_name)

    async def regenerate_master(self) -> str:
        """Regenerates the master API key.
        """

        key = token_urlsafe(24)

        query = api_key_table.update().values(
            api_key=key,
            timestamp=datetime.now()
        ).where(
            and_(
                api_key_table.c.community_name == self.community_name,
                api_key_table.c.master == 1
            )
        )

        await Sessions.database.execute(query=query)

        return key

    async def exists(self) -> bool:
        """Checks if community exists with name.
        """

        query = select([func.count()]).select_from(community_table).where(
            community_table.c.community_name == self.community_name
        )

        return await Sessions.database.fetch_val(query=query) > 0

    async def matches(self, search: str = None,
                      page: int = 1, limit: int = 10, desc: bool = True,
                      require_scoreboard: bool = True
                      ) -> AsyncGenerator[MatchModel, Match]:
        """Lists matches.

        Paramters
        ---------
        search: str
        page: int
        limit: int
        desc: bool, optional
            by default True
        require_scoreboard : bool, optional
            If enabled scoreboard will need to be ready
            to pull match, by default True

        Yields
        ------
        MatchModel
            Holds basic match details.
        Match
            Used for interacting with a match.
        """

        query = select([
            scoreboard_total_table.c.match_id,
            scoreboard_total_table.c.timestamp,
            scoreboard_total_table.c.status,
            scoreboard_total_table.c.demo_status,
            scoreboard_total_table.c.map,
            scoreboard_total_table.c.team_1_name,
            scoreboard_total_table.c.team_2_name,
            scoreboard_total_table.c.team_1_score,
            scoreboard_total_table.c.team_2_score,
            scoreboard_total_table.c.team_1_side,
            scoreboard_total_table.c.team_2_side,
            scoreboard_total_table.c.community_name
        ])

        if search:
            like_search = "%{}%".format(search)

            query = query.select_from(
                scoreboard_total_table.join(
                    scoreboard_table,
                    scoreboard_table.c.match_id ==
                    scoreboard_total_table.c.match_id
                ).join(
                    user_table,
                    user_table.c.steam_id == scoreboard_table.c.steam_id
                )
            ).where(
                and_(
                    scoreboard_total_table.c.community_name ==
                    self.community_name,
                    or_(
                        scoreboard_total_table.c.match_id == search,
                        scoreboard_total_table.c.map.like(like_search),
                        scoreboard_total_table.c.team_1_name.like(
                            like_search),
                        scoreboard_total_table.c.team_2_name.like(
                            like_search),
                        user_table.c.name.like(like_search),
                        user_table.c.steam_id == search
                    )
                )
            )
        elif require_scoreboard:
            query = query.select_from(
                scoreboard_total_table.join(
                    scoreboard_table,
                    scoreboard_table.c.match_id ==
                    scoreboard_total_table.c.match_id
                )
            ).where(
                scoreboard_total_table.c.community_name
                == self.community_name,
            )
        else:
            query = query.select_from(
                scoreboard_total_table
            ).where(
                scoreboard_total_table.c.community_name
                == self.community_name,
            )

        query = query.distinct().order_by(
            scoreboard_total_table.c.timestamp.desc() if desc
            else scoreboard_total_table.c.timestamp.asc()
        ).limit(limit).offset((page - 1) * limit if page > 1 else 0)

        async for row in Sessions.database.iterate(query=query):
            yield MatchModel(**row), self.match(row["match_id"])

    async def public(self) -> PublicCommunityModel:
        """Used to get public data on a community.

        Returns
        -------
        PublicCommunityModel

        Raises
        ------
        InvalidCommunity
            Raised when community ID doesn't exist.
        """

        query = select([
            community_table.c.owner_id,
            community_table.c.disabled,
            community_table.c.community_name,
            community_table.c.timestamp,
            community_table.c.banned
        ]).select_from(community_table).where(
            community_table.c.community_name == self.community_name
        )

        row = await Sessions.database.fetch_one(query)
        if row:
            return PublicCommunityModel(**row)
        else:
            raise InvalidCommunity()

    async def get(self) -> CommunityModel:
        """Gets base community details.

        Returns
        -------
        CommunityModel
            Holds community data.

        Raises
        ------
        InvalidCommunity
            Raised when community ID doesn't exist.
        """

        query = select([
            api_key_table.c.api_key,
            api_key_table.c.owner_id,
            community_table.c.disabled,
            community_table.c.banned,
            community_table.c.community_name,
            community_table.c.timestamp,
            community_table.c.allow_api_access,
            community_table.c.match_start_webhook,
            community_table.c.round_end_webhook,
            community_table.c.match_end_webhook,
            community_table.c.customer_id,
            community_table.c.email,
            community_table.c.card_id,
            payment_table.c.max_upload,
            payment_table.c.amount,
            payment_table.c.payment_status,
            payment_table.c.cancelled,
        ]).select_from(
            community_table.join(
                api_key_table,
                community_table.c.community_name ==
                api_key_table.c.community_name
            ).join(
                payment_table,
                and_(
                    community_table.c.community_name ==
                    payment_table.c.community_name,
                    payment_table.c.expires >= datetime.now()
                ),
                isouter=True
            )
        ).where(
            and_(
                community_table.c.community_name == self.community_name,
                api_key_table.c.master == True  # noqa: E712
            )
        ).order_by(
            payment_table.c.expires.desc()
        )

        row = await Sessions.database.fetch_one(query)
        if row:
            return CommunityModel(**row)
        else:
            raise InvalidCommunity()

    async def disable(self) -> None:
        """Disables a community, tries to cancel any active subscriptions.
        """

        try:
            await self.cancel_subscription()
        except NoActivePayment:
            pass

        query = community_table.update().where(
            community_table.c.community_name == self.community_name
        ).values(disabled=True)

        await Sessions.database.execute(query)
