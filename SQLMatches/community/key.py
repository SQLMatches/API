# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2021 WardPearce
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


from secrets import token_urlsafe
from sqlalchemy.sql import select, and_

from ..resources import Sessions
from ..tables import api_key_table


class Key:
    def __init__(self, key: str, community_name: str) -> None:
        self.key = key
        self.community_name = community_name

    @property
    def __and_statement(self) -> and_:
        return and_(
            api_key_table.c.community_name == self.community_name,
            api_key_table.c.api_key == self.key,
            api_key_table.c.master == False  # noqa: E712
        )

    async def regenerate(self) -> str:
        """Used to regenerate a key.

        Returns
        -------
        str
            New key.
        """

        key = token_urlsafe(24)

        await Sessions.database.execute(
            api_key_table.update().values(
                api_key=key
            ).where(
                self.__and_statement
            )
        )

        return key

    async def get(self) -> str:
        """Used to get key.

        Returns
        -------
        str
        """

        api_key = await Sessions.database.fetch_val(
            select([api_key_table.c.api_key]).select_from(
                api_key_table
            ).where(
                self.__and_statement
            )
        )

        return api_key
