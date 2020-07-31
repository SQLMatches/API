from starlette.endpoints import HTTPEndpoint
from ..templating import TEMPLATE


class ScoreboardPage(HTTPEndpoint):
    async def get(self, request):
        return TEMPLATE.TemplateResponse(
            "scoreboard.html",
            {"request": request}
        )
