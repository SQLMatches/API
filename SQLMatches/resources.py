from databases import Database
from .settings import DemoSettings


class Session:
    db: Database


class Config:
    demo: DemoSettings
    root_generate_hash: bytes
