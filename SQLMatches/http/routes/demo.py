from falcon import Request, Response, before

from ..hooks import required_scopes
from ...helpers.match import Match


class DemoResource:
    async def on_get(self, req: Request, resp: Response,
                     match_id: str) -> None:
        await Match(match_id).demo.download(
            resp,
            req.context.get_session("steam_id")
        )

    @before(required_scopes("demo.upload"), is_async=True)
    async def on_put(self, req: Request, resp: Response,
                     match_id: str) -> None:
        await Match(match_id).demo.save(req)

    @before(required_scopes("demo.delete"), is_async=True)
    async def on_delete(self, req: Request, resp: Response,
                        match_id: str) -> None:
        await Match(match_id).demo.delete()
