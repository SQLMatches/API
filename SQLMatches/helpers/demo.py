import aiofiles
import aiofiles.os

from falcon import Request
from falcon.errors import HTTPNotFound

from os import path

from ..resources import Config


class DemoFile:
    def __init__(self, match_id: str, req: Request) -> None:
        """Interact with the demo file.

        Parameters
        ----------
        match_id : str
        req : Request
        """

        self._match_id = match_id
        self._req = req
        self._pathway = path.join(
            Config.demo._pathway,
            match_id + Config.demo._extension
        )

    async def exists(self) -> bool:
        return await aiofiles.os.path.exists(self._pathway)  # type: ignore

    async def save(self) -> None:
        size = 0

        async with aiofiles.open(self._pathway, "wb") as f_:
            async for chunk in self._req.stream:
                size += len(chunk)
                await f_.write(chunk)

    async def delete(self) -> None:
        if not await self.exists():
            raise HTTPNotFound(
                title="Match ID not found",
                description=f"Match with ID {self._match_id} doesn't exist"
            )

        await aiofiles.os.remove(self._pathway)
