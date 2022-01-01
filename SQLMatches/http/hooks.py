from bcrypt import checkpw
from falcon import Request, Response, HTTPUnauthorized

from ..helpers.basic_auth import request_to_basic_auth
from ..resources import Config


def root_generate(req: Request, resp: Response, resource, params) -> None:
    _, password = request_to_basic_auth(req)

    if not checkpw(password.encode(), Config.root_generate_hash):
        raise HTTPUnauthorized()
