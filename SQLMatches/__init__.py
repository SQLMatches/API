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


import logging
import bcrypt
import backblaze

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from typing import Dict, List, Tuple

from databases import Database
from aiohttp import ClientSession
from aiojobs import create_scheduler
from aiocache import Cache

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from .tables import create_tables
from .resources import Sessions, Config
from .settings import (
    DatabaseSettings,
    B2UploadSettings,
    LocalUploadSettings
)
from .middlewares import APIAuthentication

from .routes import ROUTES, ERROR_HANDLERS
from .routes.errors import auth_error

from .garbage import GRABAGE_HANDLERS_TO_SPAWN

from .misc import cache_community_types, SessionKey

from .constants import MAP_IMAGES, COMMUNITY_TYPES


__version__ = "0.1.0"
__url__ = "https://github.com/WardPearce/SQLMatches"
__description__ = """
SQLMatches is a free & open source software built around
giving players & communities easy access to match records & demos.
"""
__author__ = "WardPearce"
__author_email__ = "wardpearce@protonmail.com"
__license__ = "GPL v3"


logger = logging.getLogger("SQLMatches")


class SQLMatches(Starlette):
    def __init__(self, database_settings: DatabaseSettings,
                 friendly_url: str,
                 root_steam_id: str,
                 upload_settings: Tuple[
                     B2UploadSettings, LocalUploadSettings] = None,
                 map_images: Dict[str, str] = MAP_IMAGES,
                 upload_delay: float = 0.00001,
                 free_upload_size: float = 50.0,
                 max_upload_size: float = 100.0,
                 cost_per_mb: float = 0.15,
                 timestamp_format: str = "%m/%d/%Y-%H:%M:%S",
                 community_types: List[str] = COMMUNITY_TYPES,
                 webhook_timeout: float = 3.0,
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
        root_steam_id: str
            Steam ID 64 to give root access.
        map_images: dict
            Key as actual map name, value as image name.
        upload_delay: float
            by default 0.1
        free_upload_size: float
            by default 50.0
        max_upload_size: float
            by default 100.0
        timestamp_format: str
        community_types: list
            List of community types.
        kwargs
        """

        startup_tasks = [self._startup]
        shutdown_tasks = [self._shutdown]

        if "on_startup" in kwargs:
            startup_tasks = startup_tasks + kwargs["on_startup"]

        if "on_shutdown" in kwargs:
            shutdown_tasks = shutdown_tasks + kwargs["on_shutdown"]

        session_key = SessionKey()
        secret_key = session_key.load()
        if not secret_key:
            secret_key = session_key.save()

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
        Config.free_upload_size = free_upload_size
        Config.max_upload_size = max_upload_size
        Config.cost_per_mb = cost_per_mb
        Config.timestamp_format = timestamp_format
        Config.root_steam_id_hashed = bcrypt.hashpw(
            root_steam_id.encode(), bcrypt.gensalt()
        )
        Config.webhook_timeout = webhook_timeout

        self.community_types = community_types

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

                logger.warning(
                    "Using local storage for demos, use b2 for production."
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

        try:
            Sessions.cache = Cache(Cache.REDIS)
            await Sessions.cache.exists("connection")
        except ConnectionRefusedError:
            Sessions.cache = Cache(Cache.MEMORY)
            logger.warning(
                "Memory cache being used, use redis for production."
            )

        if Config.upload_type == B2UploadSettings:
            await self.b2.authorize()

        self.grabage = await create_scheduler()
        for to_spawn in GRABAGE_HANDLERS_TO_SPAWN:
            await self.grabage.spawn(to_spawn())

        await cache_community_types(self.community_types)

    async def _shutdown(self) -> None:
        """Closes any underlying sessions.
        """

        await Sessions.database.disconnect()
        await Sessions.aiohttp.close()
        await Sessions.cache.close()

        if Config.upload_type == B2UploadSettings:
            await self.b2.close()

        await self.grabage.close()
