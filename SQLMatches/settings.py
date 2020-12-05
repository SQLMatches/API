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

from os import path, mkdir

from .exceptions import UnSupportedEngine
from .resources import Config


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
        """Database settings.

        Parameters
        ----------
        username : str
        password : str
        server : str
        port : int
        database : str
        engine : str, optional
            by default "mysql"

        Raises
        ------
        UnSupportedEngine
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

        Config.db_engine = engine


class B2UploadSettings:
    def __init__(self, key_id: str, application_key: str,
                 bucket_id: str, pathway: str, cdn_url: str) -> None:
        """B2 Settings

        Parameters
        ----------
        key_id: str
            B2 key ID.
        application_key: str
            B2 app key.
        bucket_id: str
            Bucket to upload demos to.
        pathway: str
            Pathway to store demos to.
        cdn_url: str
            URL to access files.
        """

        self.key_id = key_id
        self.application_key = application_key
        self.bucket_id = bucket_id
        self.cdn_url = cdn_url if cdn_url[-1:] == "/" else cdn_url + "/"
        self.pathway = pathway if pathway[-1:] == "/" else pathway + "/"


class LocalUploadSettings:
    def __init__(self, pathway: str = None) -> None:
        """Used to upload demos locally, not recommend!

        Parameters
        ----------
        pathway : str
            Pathway to upload to from package location, by default None
        """

        if pathway:
            self.pathway = pathway
        else:
            self.pathway = path.join(
                path.dirname(path.realpath(__file__)),
                "/demos"
            )

        if not path.exists(self.pathway):
            mkdir(self.pathway)


class MemoryCacheSettings:
    def __init__(self) -> None:
        """Caches into memory, shouldn't be used for production.
        """

        super().__init__()


class RedisCacheSettings:
    def __init__(self, server: str, port: int, database: int = 1,
                 pool_size: int = 1) -> None:
        """Caches to redis, production use!

        Parameters
        ----------
        server : str
        port : int
        database : int, optional
            by default 1
        pool_size : int, optional
            by default 1
        """

        self.connection_str = "redis://{}:{}/{}?pool_min_size={}".format(
            server, port, database, pool_size
        )
