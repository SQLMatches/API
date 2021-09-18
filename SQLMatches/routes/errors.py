from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from .responder import error_response


def server_error(request: Request, exc: HTTPException) -> JSONResponse:
    return error_response(
        error=exc.detail,
        status_code=exc.status_code
    )
