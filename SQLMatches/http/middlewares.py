from ..resources import Session


class SessionComponent:
    async def process_startup(self, scope, event) -> None:
        await Session.db.connect()

    async def process_shutdown(self, scope, event) -> None:
        await Session.db.disconnect()
