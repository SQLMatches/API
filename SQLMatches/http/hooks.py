from typing import Callable, List, Union
from bcrypt import checkpw
from falcon import Request, Response, HTTPUnauthorized
from sqlalchemy import select

from ..helpers.basic_auth import request_to_basic_auth
from ..resources import Config, Session
from ..tables import api_key_table


def root_required(req: Request, resp: Response, resource, params) -> None:
    _, password = request_to_basic_auth(req)

    if not checkpw(password.encode(), Config.root_generate_hash):
        raise HTTPUnauthorized()


def required_scopes(scopes: Union[List[str], str]) -> Callable:
    """Used to validate API key has scopes.

    Parameters
    ----------
    scopes : Union[List[str], str]

    Returns
    -------
    Callable

    Raises
    ------
    HTTPUnauthorized
    """

    scopes = [scopes] if isinstance(scopes, str) else list(scopes)

    async def hook_(req: Request, resp: Response, resource, params) -> None:
        steam_id, api_key = request_to_basic_auth(req)

        row = await Session.db.fetch_one(
            select(
                [api_key_table.c.scopes, api_key_table.c.api_key]
            ).select_from(api_key_table).where(
                api_key_table.c.steam_id == steam_id
            )
        )

        if (not row or not row["scopes"] or
            not checkpw(api_key.encode(), row["api_key"].encode())
                or row["scopes"].strip(",") not in scopes):
            raise HTTPUnauthorized()

        req.context.steam_id = steam_id

    return hook_
