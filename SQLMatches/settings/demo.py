from typing import Optional
from os import path, mkdir


class DemoSettings:
    def __init__(self, pathway: Optional[str] = None) -> None:
        """Initialize the demo directory.

        Parameters
        ----------
        pathway : Optional[str], optional
            by default None
        """

        if pathway:
            self._pathway = pathway
        else:
            self._pathway = path.join(
                path.abspath(path.dirname(__file__)),
                "demos"
            )

        if not path.exists(self._pathway):
            mkdir(self._pathway)
