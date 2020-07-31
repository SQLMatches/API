from starlette.applications import Starlette

from .routes import ROUTES


class SQLMatches(Starlette):
    def __init__(self, *args, **kwargs) -> None:
        Starlette.__init__(
            self,
            routes=ROUTES,
            *args,
            **kwargs
        )
