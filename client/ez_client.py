import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Union

try:
    from utilsx.console import Prettier, Colors
except ModuleNotFoundError:
    print("UtilsX not detected, installing...")
    from os import system

    system("pip install utilsx")
    print("UtilsX successfully installed!\n")
    from utilsx.console import Prettier, Colors

from datetime import datetime
from sys import exit

from library import ChatClient, listener


def color(c: Colors, v: Union[int, str]):
    return f"{c.value}{v}{Colors.default.value}"


class EzClient(ChatClient):
    def __init__(self):
        super().__init__()
        self.pp = Prettier(auto_strip_message=True)
        self.__loop = None

    @listener
    async def on_ready(self):
        self.pp.print("Joined the conversation!", datetime.now())
        self.__loop = asyncio.get_event_loop()
        self.__loop.create_task(self.handle_commands())

    async def handle_commands(self):
        while True:
            command = await self.async_input()
            if command == "":
                continue
            elif command == "help":
                self.pp.print("\nEzChat - Help\n"
                              "  say <message> | Send a message\n"
                              "  stop          | Stop the client.\n")
            elif command == "stop":
                self.pp.print(f"Exiting client...", datetime.now())
                await self.close()
                self.pp.print("Successfully exited the client!", datetime.now())
                try:
                    self.__loop.stop()
                    self.__loop.close()
                except RuntimeError:
                    pass

                exit()
            else:
                command = command.split(" ")
                if command[0] == "say":
                    command.pop(0)
                    message = " ".join(command)
                    await self.send(message)
                    self.pp.print(f"{color(Colors.light_yellow, 'YOU')}: {message}", datetime.now())
                else:
                    self.pp.print("Unknown command, use 'help' to see all the commands!", datetime.now())

    @staticmethod
    async def async_input(prompt: str = "") -> str:
        with ThreadPoolExecutor(1, "AsyncInput") as executor:
            return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)

    @listener
    async def on_message(self, member: int, message: str):
        self.pp.print(f"{color(Colors.light_cyan, member)}: {message}", datetime.now())

    @listener
    async def on_member_join(self, member: int):
        self.pp.print(f"A member with ID '{color(Colors.light_blue, member)}' joined the conversation!", datetime.now())

    @listener
    async def on_member_leave(self, member: int):
        self.pp.print(f"The member with ID '{color(Colors.light_red, member)}' left the conversation!", datetime.now())


if __name__ == "__main__":
    EzClient().run()
