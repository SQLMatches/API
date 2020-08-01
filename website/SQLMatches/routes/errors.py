from ..templating import TEMPLATE


async def not_found(request, exc):
    return TEMPLATE.TemplateResponse("error.html", {
        "request": request,
        "error": exc
    })


async def server_error(request, exc):
    return TEMPLATE.TemplateResponse("error.html", {
        "request": request,
        "error": exc
    })
