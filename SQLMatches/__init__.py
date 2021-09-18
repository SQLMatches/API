# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

import bcrypt
import aiojobs

from starlette.applications import Starlette

from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from typing import Dict
from databases import Database
from aiohttp import ClientSession

from .resources import Sessions, Config
from .constants import MAP_IMAGES
from .key_loader import KeyLoader
from .tables import create_tables
from .misc import add_slash

from .authentication import BasicAuthBackend

from .routes import ROUTES, ERROR_HANDLERS
from .routes.specs import API
from .routes.errors import auth_error


__version__ = "1.0.0"
__url__ = "https://github.com/SQLMatches"
__description__ = "CS: GO match, demo & player statistics recorder."
__author__ = "WardPearce"
__author_email__ = "wardpearce@protonmail.com"
__license__ = "GNU Affero General Public License v3.0"


class SQLMatches(Starlette):
    def __init__(self,
                 database: Database,
                 frontend_url: str,
                 backend_url: str,
                 root_steam_id: str,
                 map_images: Dict[str, str] = MAP_IMAGES,
                 **kwargs) -> None:
        self._database = database

        # Create needed tables.
        create_tables(str(self._database.url))

        # Needed middlewares
        middlewares = [
            Middleware(
                SessionMiddleware,
                secret_key=KeyLoader(name="session").load()
            ),
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            ),
            Middleware(
                AuthenticationMiddleware,
                backend=BasicAuthBackend(),
                on_error=auth_error
            )
        ]

        # Check if any used kwargs passed
        if "middleware" in kwargs:
            middlewares += kwargs["middleware"]
            kwargs.pop("middleware")

        if "routes" in kwargs:
            routes = kwargs["routes"] + ROUTES
            kwargs.pop("routes")
        else:
            routes = ROUTES

        if "exception_handlers" in kwargs:
            exception_handlers = {
                **kwargs["exception_handlers"],
                **ERROR_HANDLERS
            }
            kwargs.pop("exception_handlers")
        else:
            exception_handlers = ERROR_HANDLERS

        startup_tasks = [self._startup]
        shutdown_tasks = [self._shutdown]

        if "on_startup" in kwargs:
            startup_tasks += kwargs["on_startup"]
            kwargs.pop("on_startup")

        if "on_shutdown" in kwargs:
            shutdown_tasks += kwargs["on_shutdown"]
            kwargs.pop("on_shutdown")

        # Add some data into singletons
        Config.map_images = map_images
        Config.root_steam_id_hash = bcrypt.hashpw(
            root_steam_id.encode(), bcrypt.gensalt()
        )

        Config.frontend_url = add_slash(frontend_url)
        Config.backend_url = add_slash(backend_url)

        super().__init__(
            routes=routes,
            exception_handlers=exception_handlers,  # type: ignore
            middleware=middlewares,
            on_startup=startup_tasks,
            on_shutdown=shutdown_tasks,
            **kwargs
        )

        # Anything what requires the Starlette instance should be
        # ran under neath super

        # Register spectree to app
        API.register(self)

    async def _startup(self) -> None:
        """Creates needed sessions in context of event loop.
        """

        await self._database.connect()

        Sessions.db = self._database
        Sessions.requests = ClientSession()
        Sessions.scheduler = aiojobs.create_scheduler()

    async def _shutdown(self) -> None:
        """Closes created sessions.
        """

        await self._database.disconnect()
        await Sessions.requests.close()
        await Sessions.scheduler.close()
