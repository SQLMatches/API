class SQLMatchesError(Exception):
    def __init__(self, msg: str = "Internal error", status_code: int = 500,
                 *args: object) -> None:
        """Base error for SQLMatches.

        Parameters
        ----------
        msg : str, optional
            Human friendly error message, by default "Internal error"
        status_code : int, optional
            HTTP error code, by default 500
        """

        self.status_code = status_code
        super().__init__(msg, *args)


class MatchError(SQLMatchesError):
    def __init__(self, msg: str = "Match error", status_code: int = 500,
                 *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)


class MatchIdError(MatchError):
    def __init__(self, msg: str = "Match ID not found", status_code: int = 404,
                 *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)
