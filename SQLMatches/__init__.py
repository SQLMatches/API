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


from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from typing import Dict, Tuple

from secrets import token_urlsafe

from databases import Database
from aiohttp import ClientSession
from aiojobs import create_scheduler

import backblaze
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from .tables import create_tables
from .resources import Sessions, Config
from .settings import DatabaseSettings, B2UploadSettings, LocalUploadSettings
from .middlewares import APIAuthentication

from .routes import ROUTES, ERROR_HANDLERS
from .routes.errors import auth_error

from .grabage import GRABAGE_HANDLERS_TO_SPAWN


__version__ = "0.1.0"
__url__ = "https://github.com/WardPearce/SQLMatches"
__description__ = """
SQLMatches is a free & open source software built around
giving players & communities easy access to match records & demos.
"""
__author__ = "WardPearce"
__author_email__ = "wardpearce@protonmail.com"
__license__ = "GPL v3"


MAP_IMAGES = {
    "de_austria": "austria.jpg",
    "de_cache": "cache.jpg",
    "de_canals": "canals.jpg",
    "de_cbble": "cbble.jpg",
    "de_dust": "dust.jpg",
    "de_dust2": "dust2.jpg",
    "de_inferno": "inferno.jpg",
    "de_mirage": "mirage.jpg",
    "de_nuke": "nuke.jpg",
    "de_overpass": "overpass.jpg",
    "de_train": "train.jpg",
}


class SQLMatches(Starlette):
    def __init__(self, database_settings: DatabaseSettings,
                 friendly_url: str,
                 upload_settings: Tuple[
                     B2UploadSettings, LocalUploadSettings] = None,
                 secret_key: str = token_urlsafe(),
                 map_images: Dict[str, str] = MAP_IMAGES,
                 upload_delay: float = 0.001,
                 max_upload_size: int = 80000000,
                 timestamp_format: str = "%m/%d/%Y-%H:%M:%S",
                 ws_loop_time: float = 8.0,
                 **kwargs) -> None:
        """SQLMatches API.

        Parameters
        ----------
        database_settings: DatabaseSettings
            Holds settings for database.
        upload_settings: (B2UploadSettings, LocalUploadSettings)
            by default None
        friendly_url: str
            URL to project.
        secret_key: str
            Optionally pass your own url safe secret key.
        map_images: dict
            Key as actual map name, value as image name.
        upload_delay: float
            by default 0.1
        max_upload_size: int
            by default 80000000
        timestamp_format: str
        ws_loop_time: int
            How often to check ws connection, by default 8.0
        kwargs
        """

        startup_tasks = [self._startup]
        shutdown_tasks = [self._shutdown]

        if "on_startup" in kwargs:
            startup_tasks = startup_tasks + kwargs["on_startup"]

        if "on_shutdown" in kwargs:
            shutdown_tasks = shutdown_tasks + kwargs["on_shutdown"]

        middlewares = [
            Middleware(SessionMiddleware, secret_key=secret_key),
            Middleware(AuthenticationMiddleware, backend=APIAuthentication(),
                       on_error=auth_error),
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"]
            )
        ]

        if "middleware" in kwargs:
            middlewares = middlewares + kwargs["middleware"]

        if "routes" in kwargs:
            routes = kwargs["routes"] + ROUTES
        else:
            routes = ROUTES

        if "exception_handlers" in kwargs:
            exception_handlers = kwargs["exception_handlers"] + ERROR_HANDLERS
        else:
            exception_handlers = ERROR_HANDLERS

        if friendly_url[:1] != "/":
            friendly_url += "/"

        Config.url = friendly_url
        Config.map_images = map_images
        Config.upload_delay = upload_delay
        Config.max_upload_size = max_upload_size
        Config.timestamp_format = timestamp_format
        Config.ws_loop_time = ws_loop_time

        database_url = "://{}:{}@{}:{}/{}?charset=utf8mb4".format(
            database_settings.username,
            database_settings.password,
            database_settings.server,
            database_settings.port,
            database_settings.database
        )

        Sessions.database = Database(
            database_settings.engine + database_url
        )

        if upload_settings:
            if isinstance(upload_settings, B2UploadSettings):
                Config.demo_pathway = upload_settings.pathway
                Config.cdn_url = upload_settings.cdn_url
                Config.upload_type = B2UploadSettings

                self.b2 = backblaze.Awaiting(
                    upload_settings.key_id,
                    upload_settings.application_key
                )

                Sessions.bucket = self.b2.bucket(
                    upload_settings.bucket_id
                )
            elif isinstance(upload_settings, LocalUploadSettings):
                Config.demo_pathway = upload_settings.pathway
                Config.cdn_url = None
                Config.upload_type = LocalUploadSettings

                routes.append(
                    Mount(
                        "/demos",
                        StaticFiles(directory=upload_settings.pathway),
                        name="demos"
                    )
                )
        else:
            Config.upload_type = None

        create_tables(
            "{}+{}{}".format(
                database_settings.engine,
                database_settings.alchemy_engine,
                database_url
            )
        )

        super().__init__(
            routes=routes,
            exception_handlers=exception_handlers,
            middleware=middlewares,
            on_startup=startup_tasks,
            on_shutdown=shutdown_tasks,
            **kwargs
        )

    async def _startup(self) -> None:
        """Starts up needed sessions.
        """

        await Sessions.database.connect()
        Sessions.aiohttp = ClientSession()

        if Config.upload_type == B2UploadSettings:
            await self.b2.authorize()

        self.grabage = await create_scheduler()

        for to_spawn in GRABAGE_HANDLERS_TO_SPAWN:
            await self.grabage.spawn(to_spawn())

    async def _shutdown(self) -> None:
        """Closes any underlying sessions.
        """

        await Sessions.database.disconnect()
        await Sessions.aiohttp.close()

        if Config.upload_type == B2UploadSettings:
            await self.b2.close()

        await self.grabage.close()
