# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""


def add_slash(url: str) -> str:
    """Adds slash to url

    Parameters
    ----------
    url : str

    Returns
    -------
    str
    """
    if url[:1] != "/":
        url += "/"

    return url
