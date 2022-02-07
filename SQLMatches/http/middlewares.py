from aiohttp import ClientSession

from ..resources import Session


class SessionComponent:
    async def process_startup(self, scope, event) -> None:
        await Session.db.connect()
        Session.requests = ClientSession()

    async def process_shutdown(self, scope, event) -> None:
        await Session.db.disconnect()
        await Session.requests.close()
