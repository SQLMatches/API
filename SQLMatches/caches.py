# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2020 WardPearce
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


from typing import Any
from .resources import Sessions


class CacheBase:
    def __init__(self, key: str) -> None:
        self.key = key

    async def expire(self) -> None:
        await Sessions.cache.delete(self.key)

    async def set(self, value: Any, ttl=None) -> None:
        await Sessions.cache.set(self.key, value, ttl=ttl)

    async def get(self) -> Any:
        return await Sessions.cache.get(self.key)


class __ScoreboardCache:
    def scoreboard(self, match_id: str) -> CacheBase:
        return CacheBase(self.key + "-" + match_id)


class __MatchesCache:
    def matches(self) -> CacheBase:
        return CacheBase(self.key + "-matches")


class __ProfileCache:
    def profile(self, steam_id: str) -> CacheBase:
        return CacheBase(self.key + steam_id)


class CommunityCache(CacheBase, __MatchesCache, __ScoreboardCache,
                     __ProfileCache):
    def __init__(self, community_name: str) -> None:
        super().__init__(community_name)

    def stats(self, key: str = "-stats") -> CacheBase:
        return CacheBase(self.key + key)

    def payments(self, key: str = "-payments") -> CacheBase:
        return CacheBase(self.key + key)


class CommunitiesCache(CacheBase, __MatchesCache):
    def __init__(self, key: str = "communities") -> None:
        super().__init__(key)


class VersionCache(CacheBase):
    def __init__(self, version: str) -> None:
        super().__init__("version-" + version)
