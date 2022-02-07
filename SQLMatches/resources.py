from databases import Database
from aiohttp import ClientSession

from .settings import DemoSettings, SteamSettings


class Session:
    db: Database
    requests: ClientSession


class Config:
    demo: DemoSettings
    steam: SteamSettings
    root_generate_hash: bytes
