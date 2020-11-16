# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2020 WardPearce
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


from starlette.requests import Request

from ..api import error_response


def server_error(request: Request, exc) -> error_response:
    return error_response(
        error=exc.detail,
        status_code=exc.status_code
    )


def auth_error(request: Request, exc: Exception) -> error_response:
    return error_response(
        error=str(exc),
        status_code=401
    )


def internal_error(request: Request, exc: Exception) -> error_response:
    return error_response(
        error=str(exc),
        status_code=500
    )


def payload_error(request: Request, exc) -> error_response:
    return error_response(
        error=exc.messages,
        status_code=exc.status_code,
        headers=exc.headers
    )


def rate_limted_error(request: Request, exc) -> error_response:
    return error_response(
        error="Rate limit exceeded: {}".format(exc.detail),
        status_code=429
    )
