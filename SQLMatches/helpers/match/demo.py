import aiofiles
import aiofiles.os

from falcon import Request, Response

from sqlalchemy import select
from os import path
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from uuid import uuid4

from ...resources import Session
from ...tables import scoreboard_total_table, demo_log_table
from ...errors import DemoNotFound
from ...env import DEMO_SETTINGS


if TYPE_CHECKING:
    from . import Match


class DemoFile:
    def __init__(self, upper: "Match") -> None:
        """Interact with the demo file.

        Parameters
        ----------
        upper : Match
        """

        self.__upper = upper
        self._pathway = path.join(
            DEMO_SETTINGS._pathway,
            self.__upper.match_id + DEMO_SETTINGS._extension
        )

    async def __update_match(self, **kwargs) -> None:
        await Session.db.execute(
            scoreboard_total_table.update(**kwargs).where(
                scoreboard_total_table.c.match_id == self.__upper.match_id
            )
        )

    async def __exist_raise(self) -> None:
        """Raise a DemoNotFound if the demo doesn't exist.

        Raises
        ------
        DemoNotFound
        """

        if not await self.exists():
            raise DemoNotFound()

    async def exists(self) -> bool:
        """Return True if the path exists False otherwise.

        Returns
        -------
        bool
        """

        return await aiofiles.os.path.exists(self._pathway)  # type: ignore

    async def download(self, resp: Response,
                       steam_id: Optional[str] = None) -> None:
        """Stream the demo to client.

        Parameters
        ----------
        resp : Response
        steam_id : str, optional
            If provided download will be logged, by default None

        Raises
        ------
        DemoNotFound
        """

        await self.__exist_raise()

        if steam_id is not None:
            await Session.db.execute(demo_log_table.insert().values(
                match_id=self.__upper.match_id,
                steam_id=steam_id,
                downloaded=datetime.now(),
                log_id=str(uuid4())
            ))

        demo_size = await Session.db.fetch_val(
            select([scoreboard_total_table.c.demo_size]).select_from(
                scoreboard_total_table
            ).where(
                scoreboard_total_table.c.match_id == self.__upper.match_id
            )
        )

        resp.content_length = str(demo_size) if demo_size is not None else None
        resp.stream = await aiofiles.open(self._pathway, "rb")  # falcon magic

    async def save(self, req: Request) -> None:
        """Save the match to the local path.

        Parameters
        ----------
        req : Request
        """

        await self.__update_match(demo_status=1)

        size = 0
        async with aiofiles.open(self._pathway, "wb") as f_:
            async for chunk in req.stream:
                size += len(chunk)
                await f_.write(chunk)

        await self.__update_match(demo_size=size, demo_status=2)

    async def delete(self) -> None:
        """Delete the match from disk.

        Raises
        ------
        DemoNotFound
        """

        await self.__exist_raise()
        await aiofiles.os.remove(self._pathway)
        await self.__update_match(demo_size=0, demo_status=3)
