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


from .exceptions import UnSupportedEngine


class DatabaseSettings:
    def __init__(
                self,
                username: str,
                password: str,
                server: str,
                port: int,
                database: str,
                engine: str = "mysql"
                ) -> None:
        """
        A class for creating a URL for the Database.
        Attributes
        ----------
        username: str
            Database username.
        password: str
            Password for user.
        server: str
            Address for database server.
        port: int
            Database server port.
        database: str
            Name of database.
        engine: str
            Database's engine (Defaults 'mysql').
        """

        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.database = database
        self.engine = engine

        if engine == "mysql":
            self.alchemy_engine = "pymysql"
        elif engine == "sqlite":
            self.alchemy_engine = "sqlite3"
        elif engine == "postgresql":
            self.alchemy_engine = "psycopg2"
        else:
            raise UnSupportedEngine()
