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


from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from starlette_apispec import APISpecSchemaGenerator


MAP_IMAGES = {
    "de_austria": "austria.jpg",
    "de_cache": "cache.jpg",
    "de_canals": "canals.jpg",
    "de_cbble": "cbble.jpg",
    "de_dust": "dust.jpg",
    "de_dust2": "dust2.jpg",
    "de_inferno": "inferno.jpg",
    "de_mirage": "mirage.jpg",
    "de_nuke": "nuke.jpg",
    "de_overpass": "overpass.jpg",
    "de_train": "train.jpg",
}


COMMUNITY_TYPES = [
    "personal",
    "community",
    "team",
    "organization"
]


SCHEMAS = APISpecSchemaGenerator(
    APISpec(
        title="SQLMatches API",
        version="0.1.0",
        openapi_version="3.0.0",
        contact={
            "name": "WardPearce",
            "url": "https://github.com/SQLMatches",
            "email": "wardpearce@protonmail.com"
        },
        info={
            "description": """
SQLMatches is a free & open source software built around
giving players & communities easy access to match records & demos.
"""
        },
        plugins=[MarshmallowPlugin()],
    )
)
