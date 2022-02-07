from enum import Enum


class SQLMatchesErrorCodes(Enum):
    INTERNAL = 1000

    MATCH_NOT_FOUND = 2000
    MATCH_ID_TAKEN = 2001

    DEMO_NOT_FOUND = 3000


class SQLMatchesError(Exception):
    def __init__(self, msg: str = "Internal error", status_code: int = 500,
                 error_code: SQLMatchesErrorCodes = SQLMatchesErrorCodes.INTERNAL,  # noqa: E501
                 *args: object) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.msg = msg
        super().__init__(msg, *args)

    def response(self) -> dict:
        """Response data.

        Returns
        -------
        dict
        """

        return {
            "data": None,
            "error": {
                "msg": self.msg,
                "status_code": self.status_code,
                "error_code": self.error_code.value
            }
        }


class MatchError(SQLMatchesError):
    pass


class MatchNotFound(MatchError):
    def __init__(self, msg: str = "Match not found", status_code: int = 404,
                 error_code: SQLMatchesErrorCodes = SQLMatchesErrorCodes.MATCH_NOT_FOUND,  # noqa: E501
                 *args: object) -> None:
        super().__init__(msg, status_code, error_code, *args)


class MatchIdTaken(MatchError):
    def __init__(self, msg: str = "Match ID taken", status_code: int = 400,
                 error_code: SQLMatchesErrorCodes = SQLMatchesErrorCodes.MATCH_ID_TAKEN,  # noqa: E501
                 *args: object) -> None:
        super().__init__(msg, status_code, error_code, *args)


class DemoError(SQLMatchesError):
    pass


class DemoNotFound(DemoError):
    def __init__(self, msg: str = "Demo not found", status_code: int = 404,
                 error_code: SQLMatchesErrorCodes = SQLMatchesErrorCodes.DEMO_NOT_FOUND,  # noqa: E501
                 *args: object) -> None:
        super().__init__(msg, status_code, error_code, *args)
