from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from .home import HomePage
from .community import CommunityPage
from .scoreboard import ScoreboardPage

from ..resources import Config


ROUTES = [
    Route("/", HomePage, name="HomePage"),
    Mount("/{community}", routes=[
        Route("/", CommunityPage),
        Route("/{scoreboard_id}", ScoreboardPage)
    ]),
    Mount("/assets", StaticFiles(directory=Config.assets_dir), name="assets"),
]
