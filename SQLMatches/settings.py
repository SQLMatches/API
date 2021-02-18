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


class __Extension:
    def __init__(self, extension: str = ".dem.bz2") -> None:
        self.extension = extension


class B2UploadSettings(__Extension):
    def __init__(self, key_id: str, application_key: str,
                 bucket_id: str, pathway: str, cdn_url: str,
                 *args, **kwargs) -> None:
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
        extension: str,
            by default ".dem.bz2"
        """

        super().__init__(*args, **kwargs)

        self.key_id = key_id
        self.application_key = application_key
        self.bucket_id = bucket_id
        self.cdn_url = cdn_url if cdn_url[-1:] == "/" else cdn_url + "/"

        if pathway[-1:] == "/":
            pathway = pathway[:-1]

        if pathway[0] != "/":
            pathway = "/" + pathway

        self.pathway = pathway


class LocalUploadSettings(__Extension):
    def __init__(self, pathway: str = None, *args, **kwargs) -> None:
        """Used to upload demos locally, not recommend!

        Parameters
        ----------
        pathway : str
            Pathway to upload to from package location, by default None
        extension: str,
            by default ".dem.bz2"
        """

        super().__init__(*args, **kwargs)

        if pathway:
            self.pathway = pathway
        else:
            self.pathway = path.join(
                path.abspath(path.dirname(__file__)),
                "demos"
            )

        if not path.exists(self.pathway):
            mkdir(self.pathway)


class StripeSettings:
    def __init__(self, api_key: str, price_id: str,
                 testing: bool = False) -> None:
        """Used to set stripe settings.

        Parameters
        ----------
        api_key : str
            Don't include 'sk_test_' or 'sk_live_'
        price_id : str
            Stripe price ID, created on dashboard.
        testing : bool, optional
            by default False
        """

        self.api_key = api_key
        self.price_id = price_id
        self.testing = testing


class SmtpSettings:
    def __init__(self, hostname: str, port: int, use_tls: bool = True,
                 username: str = None, password: str = None) -> None:
        """SMTP Connection settings.

        Parameters
        ----------
        hostname : str
        port : int
        use_tls : bool, optional
        username : str, optional
        password : str, optional
        """

        self.hostname = hostname
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password


class WebhookSettings:
    def __init__(self, timeout: float = 3.0, match_start: str = None,
                 match_end: str = None, round_end: str = None,
                 key: str = None) -> None:
        """Used to configure webhook.

        Parameters
        ----------
        timeout : float, optional
            by default 3.0
        match_start : str, optional
            Global webhook for match start, by default None
        match_end : str, optional
            Global webhook for match end, by default None
        round_end : str, optional
            Global webhook for round end, by default None
        key : str, optional
            Global webhook key.
        """

        self.timeout = timeout
        self.match_start = match_start
        self.match_end = match_end
        self.round_end = round_end
        self.key = key
