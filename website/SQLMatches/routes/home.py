from starlette.endpoints import HTTPEndpoint
from ..templating import TEMPLATE


class HomePage(HTTPEndpoint):
    async def get(self, request):
        return TEMPLATE.TemplateResponse("home.html", {"request": request})
