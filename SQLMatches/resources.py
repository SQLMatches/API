# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from aiohttp import ClientSession
from databases import Database
from typing import Dict
from aiojobs import Scheduler


class Sessions:
    """Singleton for sessions.
    """

    requests: ClientSession
    db: Database
    scheduler: Scheduler


class Config:
    map_images: Dict[str, str]
    root_steam_id_hash: bytes
    frontend_url: str
    backend_url: str
