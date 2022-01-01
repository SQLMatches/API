import falcon
from falcon import Request, Response


def json_serialize(req: Request, resp: Response, exception) -> None:
    resp.data = exception.to_json()
    resp.content_type = falcon.MEDIA_JSON

    resp.append_header("Vary", "Accept")
