import base64
import binascii

from typing import Tuple
from falcon import Request, HTTPUnauthorized


def request_to_basic_auth(req: Request) -> Tuple[str, str]:
    """Converts request to basic auth username & password
    Parameters
    ----------
    req : Request
    Returns
    -------
    str
        username
    str
        password
    Raises
    ------
    HTTPUnauthorized
    """

    if "AUTHORIZATION" not in req.headers:
        raise HTTPUnauthorized()

    auth = req.headers["AUTHORIZATION"]
    try:
        scheme, credentials = auth.split()
        if scheme.lower() != "basic":
            raise HTTPUnauthorized()
        decoded = base64.b64decode(credentials).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error):
        raise HTTPUnauthorized()

    username, _, password = decoded.partition(":")

    return username, password
