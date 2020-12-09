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

from asyncio import sleep

from .resources import WebsocketQueue, Config, DemoQueue


async def handle_queue():
    """Handles cleaning up WS queue.
    """

    while True:
        old_scoreboards = dict(WebsocketQueue.scoreboards)
        old_matches = list(WebsocketQueue.matches)
        old_communities = list(WebsocketQueue.communities)

        # Giving the websocket a extra 5 seconds.
        await sleep(Config.ws_loop_time + 5)

        # Speed isn't really a concern here.
        # This process will only be ran once every X amount of seconds.

        for community in old_communities:
            if community in WebsocketQueue.communities:
                WebsocketQueue.communities.remove(community)

        for matches in old_matches:
            if matches in WebsocketQueue.matches:
                WebsocketQueue.matches.remove(matches)

        for scoreboard in old_scoreboards:
            for new_scoreboard in dict(WebsocketQueue.scoreboards):
                if scoreboard == new_scoreboard:
                    WebsocketQueue.scoreboards.pop(
                        scoreboard
                    )


async def demo_delete():
    """Handles deleting demos in background off local storage or B2.
    """

    while True:
        for match_id in list(DemoQueue.matches):
            DemoQueue.matches.remove(match_id)

        await sleep(10.0)


GRABAGE_HANDLERS_TO_SPAWN = [
    handle_queue,
    demo_delete
]
