import os
from dotenv import load_dotenv

from .settings import DatabaseSettings, DemoSettings, SteamSettings


load_dotenv()


DATABASE_SETTINGS = DatabaseSettings(
    os.environ["DB_USERNAME"],
    os.environ["DB_PASSWORD"],
    os.environ["DB_NAME"],
    os.getenv("DB_SERVER", "localhost"),
    int(os.getenv("DB_PORT", 3306)),
    os.getenv("DB_ENGINE", "mysql")
)


DEMO_SETTINGS = DemoSettings(
    os.getenv("DEMO_PATHWAY"),
    os.getenv("DEMO_EXT", ".dem.bz2")
)


STEAM_SETTINGS = SteamSettings(
    os.environ["STEAM_API_KEY"],
    os.getenv("STEAM_API_URL", "https://api.steampowered.com/")
)


FRONTEND_URL = os.environ["FRONTEND_URL"]
