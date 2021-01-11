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

from typing import Any, AsyncGenerator, Tuple
from sqlalchemy.sql import and_, select

from .resources import Sessions
from .tables import update_table
from .exceptions import InvalidVersion


class Version:
    def __init__(self, major: int, minor: int, patch: int) -> None:
        """Used to get & save version messages.

        Parameters
        ----------
        major : int
        minor : int
        patch : int
        """

        self.major = major
        self.minor = minor
        self.patch = patch

    @property
    def __statement(self) -> Any:
        return and_(
            update_table.c.major == self.major,
            update_table.c.minor == self.minor,
            update_table.c.patch == self.patch
        )

    async def get(self) -> str:
        """Used to get a version message.

        Returns
        -------
        str
            Version message

        Raises
        ------
        InvalidVersion
        """

        message = await Sessions.database.fetch_val(
            select([update_table.c.message]).select_from(
                update_table
            ).where(
                self.__statement
            )
        )

        if message:
            return message
        else:
            raise InvalidVersion()

    async def save(self, message: str) -> None:
        """Used to save / update a version message.

        Parameters
        ----------
        message : str
        """

        try:
            await Sessions.database.execute(
                update_table.insert().values(
                    major=self.major,
                    minor=self.minor,
                    patch=self.patch,
                    message=message
                )
            )
        except Exception:
            await Sessions.database.execute(
                update_table.update().values(
                    major=self.major,
                    minor=self.minor,
                    patch=self.patch,
                    message=message
                ).where(
                    self.__statement
                )
            )


async def versions() -> AsyncGenerator[Tuple[str, str, Version], None]:
    """Used to get versions.

    Yields
    ------
    str
        Version message.
    str
        Formatted version.
    Version
        Used to interact with version.
    """

    query = update_table.select().order_by(
        update_table.c.major.desc(),
        update_table.c.minor.desc(),
        update_table.c.patch.desc()
    )

    async for row in Sessions.database.iterate(query):
        yield row["message"], "{}.{}.{}".format(
            row["major"], row["minor"], row["patch"]
        ), Version(
            row["major"], row["minor"], row["patch"]
        )
