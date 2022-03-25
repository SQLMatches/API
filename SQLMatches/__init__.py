import uvicorn

from falcon import asgi
from bcrypt import gensalt, hashpw
from secrets import token_urlsafe
from colorama import init, Fore
from os import get_terminal_size
from databases import Database

from .resources import Config, Session
from .http import APP
from .tables import create_tables

from .env import DATABASE_SETTINGS, FRONTEND_URL


init()


__all__ = [
    "SQLMatches"
]


class SQLMatches:
    def __init__(self) -> None:
        Session.db = Database(DATABASE_SETTINGS._url)

        self.__root_generate_pass = token_urlsafe(44)
        Config.root_generate_hash = hashpw(
            self.__root_generate_pass.encode(), gensalt()
        )

        create_tables(DATABASE_SETTINGS._url)

    @property
    def root_password(self) -> str:
        """The password for the root user.

        Returns
        -------
        str
        """

        return self.__root_generate_pass

    @property
    def app(self) -> asgi.App:
        """Return the asgi application.

        Returns
        -------
        asgi.App
        """

        return APP

    def serve(self, **kwargs) -> None:
        """Serve the HTTP server.
        """

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
        print(f"{FRONTEND_URL}/root/{self.__root_generate_pass}")
        print((Fore.YELLOW + "Simply restart the web server to invalidate the"
               " current link & to generate a new one."), Fore.RESET)

        print_line()

        try:
            uvicorn.run(self.app, **kwargs)
        except KeyboardInterrupt:
            pass
