# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from uuid import uuid4 as __uuid4


def uuid4() -> str:
    return str(__uuid4())
