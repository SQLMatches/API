from urllib.parse import quote_plus


class DatabaseSettings:
    def __init__(
                self,
                username: str,
                password: str,
                database: str,
                server: str = "localhost",
                port: int = 3306,
                engine: str = "mysql"
                ) -> None:
        """Database settings.
        Parameters
        ----------
        username : str
        password : str
        database : str
        server : str, optional
            by default "localhost"
        port : int, optional
            by default 3306
        engine : str, optional
            by default "mysql"

        Raises
        ------
        UnSupportedEngine
        """

        self._url = "{}://{}:{}@{}:{}/{}?charset=utf8mb4".format(
            engine,
            username,
            quote_plus(password),
            server,
            port,
            database
        )
