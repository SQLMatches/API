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
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from typing import Dict, List, Tuple

from datetime import timedelta

from databases import Database
from aiohttp import ClientSession
from aiojobs import create_scheduler
from aiocache import Cache
from aiosmtplib import SMTP

from .stripe import Stripe

from .tables import create_tables
from .resources import Sessions, Config
from .settings import (
    DatabaseSettings,
    B2UploadSettings,
    LocalUploadSettings,
    StripeSettings,
    SmtpSettings
)
from .middlewares import APIAuthentication

from .routes import ROUTES, ERROR_HANDLERS
from .routes.errors import auth_error

from .background_tasks import TASKS_TO_SPAWN

from .misc import (
    cache_community_types,
    create_product_and_set,
    KeyLoader
)

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
    def __init__(self,
                 database_settings: DatabaseSettings,
                 stripe_settings: StripeSettings,
                 smtp_settings: SmtpSettings,
                 friendly_url: str,
                 frontend_url: str,
                 root_steam_id: str,
                 system_email: str,
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
                 match_max_length: timedelta = timedelta(hours=3),
                 payment_expires: timedelta = timedelta(days=31),
                 clear_cache: bool = True,
                 **kwargs) -> None:
        """SQLMatches API.

        Parameters
        ----------
        database_settings : DatabaseSettings
        stripe_settings : StripeSettings
        friendly_url : str
        frontend_url : str
        root_steam_id : str
        system_email : str
        upload_settings : [B2UploadSettings, LocalUploadSettings], optional
            by default None
        map_images : Dict[str, str], optional
            by default MAP_IMAGES
        upload_delay : float, optional
            by default 0.00001
        free_upload_size : float, optional
            by default 50.0
        max_upload_size : float, optional
            by default 100.0
        cost_per_mb : float, optional
            by default 0.15
        timestamp_format : str, optional
            by default "%m/%d/%Y-%H:%M:%S"
        community_types : List[str], optional
            by default COMMUNITY_TYPES
        webhook_timeout : float, optional
            by default 3.0
        match_max_length : timedelta, optional
            by default timedelta(hours=3)
        payment_expires : timedelta, optional
            by default timedelta(days=31)
        """

        startup_tasks = [self._startup]
        shutdown_tasks = [self._shutdown]

        if "on_startup" in kwargs:
            startup_tasks = startup_tasks + kwargs["on_startup"]

        if "on_shutdown" in kwargs:
            shutdown_tasks = shutdown_tasks + kwargs["on_shutdown"]

        middlewares = [
            Middleware(SessionMiddleware,
                       secret_key=KeyLoader(name="session").load()),
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

        if frontend_url[:1] != "/":
            frontend_url += "/"

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
        Config.root_webhook_key_hashed = bcrypt.hashpw(
            (KeyLoader("webhook").load()).encode(), bcrypt.gensalt()
        )
        Config.webhook_timeout = webhook_timeout
        Config.match_max_length = match_max_length
        Config.payment_expires = payment_expires
        Config.system_email = system_email
        Config.frontend_url = frontend_url
        Config.currency = stripe_settings.currency
        Config.receipt_url_base = stripe_settings.receipt_url_base

        self.community_types = community_types
        self.clear_cache = clear_cache
        self.product_name = stripe_settings.product_name

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

        create_tables(
            "{}+{}{}".format(
                database_settings.engine,
                database_settings.alchemy_engine,
                database_url
            )
        )

        Sessions.smtp = SMTP(
            hostname=smtp_settings.hostname,
            port=smtp_settings.port,
            use_tls=smtp_settings.use_tls
        )

        Sessions.stripe = Stripe(
            stripe_settings.api_key,
            stripe_settings.testing
        )

        if upload_settings:
            Config.demo_pathway = upload_settings.pathway
            Config.demo_extension = upload_settings.extension

            if isinstance(upload_settings, B2UploadSettings):
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
                Config.cdn_url = None
                Config.upload_type = LocalUploadSettings

                # Dynamically adding mount if local storage.

                # Name attribute for Mount isn't working correctly here,
                # so please don't change '/demos/'.
                for mount in routes:
                    if type(mount) == Mount and mount.name == "api":
                        mount.app.routes.append(
                            Mount(
                                "/demos/",
                                StaticFiles(directory=Config.demo_pathway)
                            )
                        )
                        break

                logger.warning(
                    "Using local storage for demos, use b2 for production."
                )
        else:
            Config.upload_type = None

        super().__init__(
            routes=routes,
            exception_handlers=exception_handlers,
            middleware=middlewares,
            on_startup=startup_tasks,
            on_shutdown=shutdown_tasks,
            **kwargs
        )

    async def _startup(self) -> None:
        """Creates needed sessions.
        """

        await Sessions.smtp.connect()
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

        if self.clear_cache:
            await Sessions.cache.clear()

        if Config.upload_type == B2UploadSettings:
            await self.b2.authorize()

        self.background_tasks = await create_scheduler()
        for to_spawn in TASKS_TO_SPAWN:
            await self.background_tasks.spawn(to_spawn())

        await cache_community_types(self.community_types)
        await create_product_and_set(self.product_name)

    async def _shutdown(self) -> None:
        """Closes any underlying sessions.
        """

        await Sessions.smtp.quit()
        await Sessions.database.disconnect()
        await Sessions.aiohttp.close()
        await Sessions.cache.close()

        if Config.upload_type == B2UploadSettings:
            await self.b2.close()

        await self.background_tasks.close()
