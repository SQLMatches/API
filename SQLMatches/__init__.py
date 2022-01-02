import uvicorn

from falcon import asgi
from bcrypt import gensalt, hashpw
from secrets import token_urlsafe
from colorama import init, Fore
from os import get_terminal_size
from databases import Database

from .settings import DemoSettings, DatabaseSettings
from .resources import Config, Session
from .http import APP

init()


__all__ = [
    "SQLMatches",
    "DatabaseSettings",
    "DemoSettings"
]


class SQLMatches:
    def __init__(self, demo_settings: DemoSettings,
                 database_settings: DatabaseSettings) -> None:
        Config.demo = demo_settings
        Session.db = Database(database_settings._url)

        self.__root_generate_pass = token_urlsafe(64)
        Config.root_generate_hash = hashpw(
            self.__root_generate_pass.encode(), gensalt()
        )

    @property
    def app(self) -> asgi.App:
        """Return the asgi application.

        Returns
        -------
        asgi.App
        """

        return APP

    def serve(self, **kwargs) -> None:
        def print_line() -> None:
            try:
                terminal_size = get_terminal_size()
            except Exception:
                pass
            else:
                print(
                    Fore.BLUE, "-" * terminal_size.columns,
                    Fore.RESET, sep=""
                )

        print_line()

        print(Fore.BLUE, r"""
 __    ____  __               _       _
/ _\  /___ \/ /   /\/\   __ _| |_ ___| |__   ___  ___
\ \  //  / / /   /    \ / _` | __/ __| '_ \ / _ \/ __|
_\ \/ \_/ / /___/ /\/\ \ (_| | || (__| | | |  __/\__ \
\__/\___,_\____/\/    \/\__,_|\__\___|_| |_|\___||___/
        """, Fore.RESET, sep="")

        print((f"\nVisit URL below to generate new {Fore.YELLOW}root accounts"
              f" {Fore.RED}(NEVER SHARE THIS URL WITH ANYONE){Fore.RESET}:"))
        print(f"<url>/root/{self.__root_generate_pass}")
        print((Fore.YELLOW + "Simply restart the app to invalidate the"
               " current link & to generate a new one."), Fore.RESET)

        print_line()

        try:
            uvicorn.run(self.app, **kwargs)
        except KeyboardInterrupt:
            pass
