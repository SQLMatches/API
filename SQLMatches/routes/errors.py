# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from .responder import error_response


def server_error(request: Request, exc: HTTPException) -> JSONResponse:
    return error_response(
        error=exc.detail,
        status_code=exc.status_code
    )


def auth_error(request: Request, exc: Exception) -> JSONResponse:
    return error_response(
        error=str(exc),
        status_code=401
    )
