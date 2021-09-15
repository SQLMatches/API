# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from spectree import SpecTree, Response, SecurityScheme

from .match import MatchCreateSpec


API = SpecTree(
    security_schemes=[
        SecurityScheme(
            name="auth_apiKey",
            data={"type": "apiKey", "name": "Authorization", "in": "header"}
        )
    ]
)


__all__ = [
    "Response",
    "MatchCreateSpec"
]
