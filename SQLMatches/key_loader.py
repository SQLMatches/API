# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from secrets import token_urlsafe
from dotenv import load_dotenv, get_key, set_key
from os import path


class KeyLoader:
    def __init__(self, name: str, pathway: str = None) -> None:
        """Used to load keys from env.

        Parameters
        ----------
        name : str
        pathway : str, optional
            by default None
        """

        self.name = name
        self.pathway = path.join(
            path.dirname(path.realpath(__file__)) if not pathway else pathway,
            ".env"
        )

        load_dotenv(self.pathway)

    def load(self) -> str:
        """Used to load a key.

        Returns
        -------
        str
            Loaded key.
        """

        key = get_key(self.pathway, self.name)
        if key:
            return key

        return self.save()

    def save(self) -> str:
        """Used to generate a key & save it.

        Returns
        -------
        str
        """

        key = token_urlsafe(48)
        set_key(self.pathway, self.name, key)  # type: ignore
        return key
