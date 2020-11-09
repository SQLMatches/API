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
import aiofiles

from starlette.requests import Request

from os import path
from backblaze.settings import PartSettings

from .community.match import Match
from .resources import Config, Sessions
from .settings import B2UploadSettings, LocalUploadSettings


class Demo:
    def __init__(self, match: Match, request: Request) -> None:
        """Wrapper for demo uploading.

        Parameters
        ----------
        match : Match
        request : Request
        """

        self.match = match
        self.request = request

        if Config.upload_type == B2UploadSettings:
            self.upload = self.__b2_upload
        elif Config.upload_type == LocalUploadSettings:
            self.upload = self.__local_upload
        else:
            self.upload = None

    async def __local_upload(self) -> bool:
        """Used to upload file locally.

        Returns
        -------
        bool
            If demo uploaded.
        """

        async with aiofiles.open(Config.demo_pathway, "wb+") as f:
            total_size = 0
            async for chunk in self.request.stream():
                await f.write(chunk)
                total_size += len(chunk)

                await asyncio.sleep(Config.upload_delay)

            if total_size > Config.max_upload_size or total_size == 0:
                await f.truncate()
                return False
            else:
                await f.close()
                return True

    async def __b2_upload(self) -> bool:
        """Used to upload demo to b2.

        Returns
        -------
        bool
            If demo uploaded.
        """

        _, file = await Sessions.bucket.create_part(PartSettings(
            path.join(
                Config.demo_pathway,
                "{}.dem".format(self.match.match_id)
            ),
            content_type="application/octet-stream"
        ))

        parts = file.parts()

        chunked = b""
        total_size = 0
        async for chunk in self.request.stream():
            chunked += chunk

            if len(chunked) >= 5000000:
                await parts.data(chunked)

                total_size += len(chunked)
                chunked = b""

            await asyncio.sleep(Config.upload_delay)

        if chunked and parts.part_number != 0:
            await parts.data(chunked)
            total_size += len(chunked)

        if total_size > Config.max_upload_size or total_size == 0:
            await file.cancel()
            return False
        else:
            await parts.finish()
            return True
