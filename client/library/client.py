import asyncio
from json import loads
from typing import Awaitable

from .exceptions import NoConnectionException

import websockets

listeners = {}


def listener(func: Awaitable):
    listeners[func.__name__] = func
    return func


class ChatClient:
    def __init__(self, *, host="ws://127.0.0.1:8080"):
        """
        Create a usable connection with a message server.

        :param host: The websocket url of the server. (default is 127.0.0.1:8080)
        """
        self.host = host
        self.__socket = None
        self.__active = False

    async def __main(self):
        """The main private instance."""

        async def execute_listener(_listener: str, *args):
            _listener = listeners.get(_listener)
            if _listener:
                await _listener(self, *args)

        async def handle_websocket(res: dict):
            if res["status"] == 200:
                await execute_listener("on_ready")
            elif res["status"] == 1000:
                await execute_listener("on_member_join", res["client_id"])
            elif res["status"] == 1001:
                await execute_listener("on_member_leave", res["client_id"])
            elif res["status"] == 1002:
                await execute_listener("on_message", res["client_id"], res["message"])

        async with websockets.connect(self.host) as ws:
            self.__socket = ws
            while self.__active:
                await handle_websocket(loads(await ws.recv()))

    def run(self):
        """Connect the client."""
        self.__active = True
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__main())
        loop.close()

    async def close(self):
        """Close the current client"""
        self.__active = False

    async def send(self, message: str):
        if not isinstance(self.__socket, websockets.WebSocketClientProtocol):
            raise NoConnectionException("No connection has been established yet. Please use the 'run' method first.")
        await self.__socket.send(message)
