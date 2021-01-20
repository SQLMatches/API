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
import logging
import aiofiles

from starlette.requests import Request
from sqlalchemy.sql import and_, select, func
from typing import Any
from datetime import datetime

from backblaze.exceptions import BackblazeException

from os import path
from backblaze.settings import PartSettings, UploadSettings

from .community.match import Match
from .resources import Config, Sessions
from .settings import B2UploadSettings, LocalUploadSettings
from .tables import scoreboard_total_table, community_table


class Demo:
    def __init__(self, match: Match, request: Request = None) -> None:
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
            self.delete = self.__b2_delete
        elif Config.upload_type == LocalUploadSettings:
            self.upload = self.__local_upload
            self.delete = self.__local_delete
        else:
            self.upload = None
            self.delete = None

    @property
    def __file_name(self) -> str:
        return self.match.match_id + Config.demo_extension

    @property
    def __demo_pathway(self) -> str:
        pathway = path.join(
            Config.demo_pathway,
            self.__file_name
        )

        if Config.upload_type == B2UploadSettings:
            # Backblaze only works with '/'
            return pathway.replace("\\", "/")

        return pathway

    @property
    def __where_statement(self) -> Any:
        return and_(
            scoreboard_total_table.c.match_id == self.match.match_id,
            scoreboard_total_table.c.community_name ==
            self.match.community_name
        )

    async def __invalid_upload(self, total_size: int) -> bool:
        """Used to see if upload size is invalid.

        Parameters
        ----------
        total_size : int
            Total size in bytes.

        Returns
        -------
        bool
            If invalid or not.
        """

        if total_size == 0:
            return False

        allow_max_upload = bool(await Sessions.database.fetch_val(
            select([func.count()]).select_from(community_table).where(
                and_(
                    community_table.c.community_name ==
                    self.match.community_name,
                    community_table.c.subscription_expires >= datetime.now()
                )
            )
        ))

        size_in_mb = total_size / 1000000

        return (
            size_in_mb > Config.max_upload_size if allow_max_upload
            else size_in_mb > Config.free_upload_size
        )

    async def __update_value(self, **kwargs) -> None:
        await Sessions.database.execute(
            scoreboard_total_table.update().values(
                **kwargs
            ).where(
                self.__where_statement
            )
        )

    async def __local_delete(self) -> bool:
        """Used to delete a local demo.

        Returns
        -------
        bool
            If demo deleted.
        """

        try:
            async with aiofiles.open(self.__demo_pathway, "wb+") as f:
                await f.truncate()
        except IOError:
            return False
        else:
            await self.__update_value(demo_status=4)
            return True

    async def __b2_delete(self) -> bool:
        b2_id = await Sessions.database.fetch_val(
            select([scoreboard_total_table.c.b2_id]).select_from(
                scoreboard_total_table
            ).where(self.__where_statement)
        )

        if not b2_id:
            return False

        try:
            await (Sessions.bucket.file(b2_id)).delete(self.__demo_pathway)
        except BackblazeException as error:
            logging.warning("Backblaze failed because of\n{}".format(error))
            return False
        else:
            await self.__update_value(demo_status=4)
            return True

    async def __local_upload(self) -> bool:
        """Used to upload file locally.

        Returns
        -------
        bool
            If demo uploaded.
        """

        assert self.request

        async with aiofiles.open(self.__demo_pathway, "wb+") as f:
            total_size = 0
            async for chunk in self.request.stream():
                await f.write(chunk)
                total_size += len(chunk)

                await asyncio.sleep(Config.upload_delay)

            if await self.__invalid_upload(total_size):
                await f.truncate()
                return False
            else:
                return True

    async def __b2_upload(self) -> bool:
        """Used to upload demo to b2.

        Returns
        -------
        bool
            If demo uploaded.
        """

        assert self.request

        content_type = "application/octet-stream"

        model, file = await Sessions.bucket.create_part(PartSettings(
            self.__demo_pathway,
            content_type=content_type
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

        if chunked:
            if parts.part_number == 0:
                await file.cancel()

                model, _ = await Sessions.bucket.upload(UploadSettings(
                    self.__demo_pathway,
                    content_type=content_type
                ), chunked)

                await self.__update_value(b2_id=model.file_id)

                return True
            else:
                await parts.data(chunked)
                total_size += len(chunked)

        if await self.__invalid_upload(total_size):
            await file.cancel()
            return False
        else:
            await parts.finish()

            await self.__update_value(b2_id=model.file_id)

            return True
