# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from spectree import SpecTree, Response

from .match import MatchCreateSpec


API = SpecTree("SQLMatches")


__all__ = [
    "Response",
    "MatchCreateSpec"
]
