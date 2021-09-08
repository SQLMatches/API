from typing import Any

from starlette.responses import JSONResponse


def response(data: Any, **kwargs) -> JSONResponse:
    return JSONResponse({"data": data, "error": None}, **kwargs)


def error_response(error: Any, **kwargs) -> JSONResponse:
    if "status_code" not in kwargs:
        kwargs["status_code"] = 500

    return JSONResponse({"data": None, "error": error}, **kwargs)
