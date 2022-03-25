from urllib.parse import quote_plus


class DatabaseSettings:
    def __init__(
                self,
                username: str,
                password: str,
                database: str,
                server: str,
                port: int,
                engine: str
                ) -> None:
        """Database settings.
        Parameters
        ----------
        username : str
        password : str
        database : str
        server : str
        port : int
        engine : str
        """

        self._url = "{}://{}:{}@{}:{}/{}?charset=utf8mb4".format(
            engine,
            username,
            quote_plus(password),
            server,
            port,
            database
        )
