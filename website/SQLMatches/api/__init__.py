from starlette.responses import JSONResponse


def error_response(error: str) -> JSONResponse:
    """
    Handles errors within the api.

    Paramters
    ---------
    error_code: str
        Same of called expection.
    """

    return JSONResponse({"data": None, "error": error})


def response(data: dict) -> JSONResponse:
    """
    Handles a successful api response.

    Paramters
    ---------
    data: dict
        Data to respond.
    """

    return JSONResponse({"data": data, "error": None})
