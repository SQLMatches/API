from starlette.endpoints import HTTPEndpoint
from ..templating import TEMPLATE


class CommunityPage(HTTPEndpoint):
    async def get(self, request):
        return TEMPLATE.TemplateResponse(
            "community.html",
            {"request": request}
        )
