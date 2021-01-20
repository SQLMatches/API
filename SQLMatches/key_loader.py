# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2021 WardPearce
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

        key = token_urlsafe()
        set_key(self.pathway, self.name, key)
        return key
