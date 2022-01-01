from falcon import Request, Response

from ...helpers.demo import DemoFile


class DemoResource:
    async def on_put(self, req: Request, resp: Response,
                     match_id: str) -> None:
        await DemoFile(match_id, req).save()

    async def on_delete(self, req: Request, resp: Response,
                        match_id: str) -> None:
        await DemoFile(match_id, req).delete()
