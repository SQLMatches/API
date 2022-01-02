import aiofiles
import aiofiles.os

from falcon import Request, Response
from falcon.errors import HTTPNotFound

from os import path

from ..resources import Config


class DemoFile:
    def __init__(self, match_id: str) -> None:
        """Interact with the demo file.

        Parameters
        ----------
        match_id : str
        req : Request
        """

        self._match_id = match_id
        self._pathway = path.join(
            Config.demo._pathway,
            match_id + Config.demo._extension
        )

    async def exists(self) -> bool:
        """Return True if the path exists False otherwise.

        Returns
        -------
        bool
        """

        return await aiofiles.os.path.exists(self._pathway)  # type: ignore

    async def download(self, resp: Response) -> None:
        resp.stream = await aiofiles.open(self._pathway, "rb")

    async def save(self, req: Request) -> None:
        """Save the demo to disk.
        """

        size = 0
        async with aiofiles.open(self._pathway, "wb") as f_:
            async for chunk in req.stream:
                size += len(chunk)
                await f_.write(chunk)

    async def delete(self) -> None:
        """Delete the match from disk.

        Raises
        ------
        HTTPNotFound
        """

        if not await self.exists():
            raise HTTPNotFound(
                title="Match ID not found",
                description=f"Match with ID {self._match_id} doesn't exist"
            )

        await aiofiles.os.remove(self._pathway)
