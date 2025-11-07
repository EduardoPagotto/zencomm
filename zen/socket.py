'''
Created on 20241001
Update on 20251030
@author: Eduardo Pagotto
'''

import os
import asyncio
import signal
from urllib.parse import urlparse

from zen import get_async_logger

class SocketServer(object):
    def __init__(self, url : str, func_handler):
        self.parsed_url = urlparse(url)
        self.func_handler = func_handler
        self.log = get_async_logger()

    async def __main_tcp(self):
        """
        Starts an asyncio TCP server.
        """
        host = self.parsed_url.hostname
        port = self.parsed_url.port

        server = await asyncio.start_server(self.func_handler, host, port)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)

        await self.log.info(f"Serving on {addrs}")

        async with server:
            await server.serve_forever()

    async def __main_unix(self):
        """
        Starts an asyncio Unix Domain Socket server.
        """
        path = self.parsed_url.path if not self.parsed_url.hostname else f'.{self.parsed_url.path}'

        if os.path.exists(path):
            os.remove(path)

        server = await asyncio.start_unix_server(self.func_handler, path)
        async with server:

            await self.log.info(f"Serving on {self.parsed_url.geturl()}")

            #await server.serve_forever()
            # Create a task for serve_forever to allow it to be cancelled
            serve_task = asyncio.create_task(server.serve_forever())

            # Set up a signal handler for graceful shutdown
            loop = asyncio.get_running_loop()
            stop_event = asyncio.Event()

            def signal_handler():
                #await self.log.warning("Shutdown signal received...")
                stop_event.set()

            loop.add_signal_handler(signal.SIGINT, signal_handler)
            loop.add_signal_handler(signal.SIGTERM, signal_handler)

            await stop_event.wait() # Wait for the shutdown signal

            self.log.info("Closing server...")
            server.close()  # Stop accepting new connections
            await server.wait_closed() # Wait for existing connections to close gracefully

            # Cancel the serve_forever task
            serve_task.cancel()
            try:
                await serve_task
            except asyncio.CancelledError:
                self.log.warning("serve_forever task cancelled")

    async def execute(self):

        if self.parsed_url.scheme == "tcp":
            return await self.__main_tcp()

        elif self.parsed_url.scheme == "unix":
            return await self.__main_unix()

        else:
            await self.log.info("Invalid SERVER_TYPE. Choose 'TCP' or 'UNIX'.")


async def socket_client(parsed_url : urlparse, timeout : int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]: # pyright: ignore[reportGeneralTypeIssues]

    if parsed_url.scheme == "tcp":

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host=parsed_url.hostname, port=parsed_url.port),
            timeout=timeout
        )

        return reader, writer

    elif parsed_url.scheme == "unix":

        final = parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}'
        reader, writer = await asyncio.wait_for(
            asyncio.open_unix_connection(path=final),
            timeout=timeout
        )

        return reader, writer

    else:
        raise Exception(f"scheme  {parsed_url.scheme} invalid")
