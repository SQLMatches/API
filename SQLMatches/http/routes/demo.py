from falcon import Request, Response, before

from ..hooks import required_scopes
from ...helpers.demo import DemoFile


class DemoResource:
    async def on_get(self, req: Request, resp: Response,
                     match_id: str) -> None:
        await DemoFile(match_id).download(resp)

    @before(required_scopes("demo.upload"), is_async=True)
    async def on_put(self, req: Request, resp: Response,
                     match_id: str) -> None:
        await DemoFile(match_id).save(req)

    @before(required_scopes("demo.delete"), is_async=True)
    async def on_delete(self, req: Request, resp: Response,
                        match_id: str) -> None:
        await DemoFile(match_id).delete()
