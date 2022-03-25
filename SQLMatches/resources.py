from databases import Database
from aiohttp import ClientSession


class Session:
    db: Database
    requests: ClientSession


class Config:
    root_generate_hash: bytes
