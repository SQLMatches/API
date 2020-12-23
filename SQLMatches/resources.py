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


import os
import socketio

from typing import Any, Dict

from backblaze.bucket.awaiting import AwaitingBucket
from aiohttp import ClientSession
from databases import Database
from aiocache import Cache
from datetime import timedelta


class Sessions:
    database: Database
    aiohttp: ClientSession
    bucket: AwaitingBucket
    cache: Cache
    websocket = socketio.AsyncServer(
        async_mode="asgi",
        cors_allowed_origins=[]
    )


class Config:
    maps_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "maps"
    )
    steam_openid_url = "https://steamcommunity.com/openid/login"

    upload_type: Any
    url: str
    map_images: str
    db_engine: str
    cdn_url: str
    demo_pathway: str
    upload_delay: float
    free_upload_size: float
    max_upload_size: float
    cost_per_mb: float
    timestamp_format: str
    root_steam_id_hashed: Any
    root_webhook_key_hashed: Any
    # Type string, type ID
    community_types: Dict[str, int] = {}
    webhook_timeout: int
    match_max_length: timedelta


class DemoQueue:
    matches: list = []
