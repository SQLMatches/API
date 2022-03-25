from typing import Optional
from os import path, mkdir


class DemoSettings:
    def __init__(self, pathway: Optional[str],
                 extension: str) -> None:
        """Initialize the demo directory.

        Parameters
        ----------
        pathway : Optional[str]
        extension: str
        """

        if pathway:
            self._pathway = pathway
        else:
            self._pathway = path.join(
                path.abspath(path.dirname(__name__)),
                "demos"
            )

        try:
            if not path.exists(self._pathway):
                mkdir(self._pathway)
        except Exception:
            pass

        self._extension = extension
