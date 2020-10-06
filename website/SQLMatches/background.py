# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2020 WardPearce
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


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

        if len(chunked) >= 5000000:
            await parts.data(chunked)

            total_size += len(chunked)
            chunked = b""

        await asyncio.sleep(Config.upload_delay)

    if chunked:
        await parts.data(chunked)
        total_size += len(chunked)

    if total_size > Config.max_upload_size or total_size == 0:
        await file.cancel()
    else:
        await parts.finish()

    await match.set_demo_status(2)
