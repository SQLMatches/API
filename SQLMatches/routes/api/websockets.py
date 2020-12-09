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


from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from websockets.exceptions import WebSocketException

from asyncio import sleep

from ...resources import Config, WebsocketQueue
from ...responses import websocket_response


class CommunityWebsocketAPI(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

        if "steam_login" in websocket.auth.scopes:
            while True:
                if WebsocketQueue.communities:
                    try:
                        await websocket.send_json(
                            websocket_response(WebsocketQueue.communities)
                        )
                    except WebSocketException:
                        break

                await sleep(Config.ws_loop_time)

        await websocket.close()
