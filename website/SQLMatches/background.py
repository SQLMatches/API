import asyncio

from starlette.requests import Request
from os import path
from backblaze.settings import PartSettings

from .community import Match
from .resources import Sessions, Config


async def upload_match_demo(request: Request, match: Match) -> None:
    """Used to upload a match demo.

    Parameters
    ----------
    request : Request
    match : Match
    """

    await match.set_demo_status(1)

    _, file = await Sessions.bucket.create_part(PartSettings(
        path.join(
            Config.demo_pathway,
            "{}.dem".format(match.match_id)
        )
    ))

    parts = file.parts()

    chunked = b""
    total_size = 0
    async for chunk in request.stream():
        chunked += chunk

        if parts.part_number != 0 or len(chunked) >= 5000000:
            await parts.data(chunked)

            total_size += len(chunked)
            chunked = b""

        await asyncio.sleep(Config.upload_delay)

    if total_size > Config.max_upload_size or total_size == 0:
        await file.cancel()
    else:
        await parts.finish()

    await match.set_demo_status(2)
