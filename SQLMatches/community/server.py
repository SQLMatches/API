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

from sqlalchemy.sql import and_

from ..resources import Sessions
from ..tables import server_table
from ..exceptions import InvalidServer

from .models import ServerModel


class Server:
    def __init__(self, ip: str, port: int, community_name: str) -> None:
        self.ip = ip
        self.port = port
        self.community_name = community_name

    @property
    def __and_statement(self) -> and_:
        return and_(
            server_table.c.ip == self.ip,
            server_table.c.port == self.port,
            server_table.c.community_name == self.community_name
        )

    async def get(self) -> ServerModel:
        """Used to get server.

        Returns
        -------
        ServerModel

        Raises
        ------
        InvalidServer
        """

        row = await Sessions.database.fetch_one(
            server_table.select().where(
                self.__and_statement
            )
        )

        if row:
            return ServerModel(**row)
        else:
            raise InvalidServer()

    async def delete(self) -> None:
        """Used to delete server.
        """

        await Sessions.database.execute(
            server_table.delete().where(
                self.__and_statement
            )
        )

    async def update(self, players: int = None,
                     max_players: int = None,
                     ip: str = None, port: int = None,
                     name: str = None, map_name: str = None) -> None:
        """Used to update server.

        Parameters
        ----------
        players : int, optional
            by default None
        max_players : int, optional
            by default None
        ip : str, optional
            by default None
        port : str, optional
            by default None
        name : str, optional
            by default None
        map_name : str, optional
            by default None
        """

        values = {}
        if players is not None:
            values["players"] = players
        if max_players is not None:
            values["max_players"] = max_players
        if port is not None:
            values["port"] = port
        if ip:
            values["ip"] = ip
        if name:
            values["name"] = name
        if map_name:
            values["map"] = map_name

        if values:
            await Sessions.database.execute(
                server_table.update().values(
                    **values
                ).where(self.__and_statement)
            )
