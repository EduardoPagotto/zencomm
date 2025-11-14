'''
Created on 20241001
Update on 20251114
@author: Eduardo Pagotto
'''

import logging
import os
import asyncio
from urllib.parse import urlparse
from functools import partial

from zencomm.utils.exceptzen import ExceptZen

class SocketServer(object):
    def __init__(self, url : str, func_handler : function):

        self.parsed_url = urlparse(url)
        self.func_handler = func_handler
        self.log = logging.getLogger(__name__)

    async def __main_tcp(self, stop_event : asyncio.Event):
        """
        Starts an asyncio TCP server.
        """
        host = self.parsed_url.hostname
        port = self.parsed_url.port

        # partial to send stop_event as first parameter
        server = await asyncio.start_server(partial(self.func_handler, stop_event), host, port)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)

        self.log.info(f"Serving on {addrs}")

        async with server:

            self.log.info(f"Serving on {self.parsed_url.geturl()}")

            serve_task = asyncio.create_task(server.serve_forever())

            await stop_event.wait() # Wait for the shutdown signal

            self.log.warning("Closing server...")
            server.close()  # Stop accepting new connections
            await server.wait_closed() # Wait for existing connections to close gracefully

            # Cancel the serve_forever task
            serve_task.cancel()
            try:
                await serve_task
            except asyncio.CancelledError:
                self.log.warning("serve_forever task cancelled")

            await serve_task

    async def __main_unix(self, stop_event : asyncio.Event):
        """
        Starts an asyncio Unix Domain Socket server.
        """
        path = self.parsed_url.path if not self.parsed_url.hostname else f'.{self.parsed_url.path}'

        if os.path.exists(path):
            os.remove(path)

        server = await asyncio.start_unix_server(partial(self.func_handler, stop_event), path)
        async with server:

            self.log.info(f"Serving on {self.parsed_url.geturl()}")

            serve_task = asyncio.create_task(server.serve_forever())

            await stop_event.wait() # Wait for the shutdown signal

            self.log.warning("Closing server...")
            server.close()  # Stop accepting new connections
            await server.wait_closed() # Wait for existing connections to close gracefully

            # Cancel the serve_forever task
            serve_task.cancel()
            try:
                await serve_task
            except asyncio.CancelledError:
                self.log.warning("serve_forever task cancelled")

    async def execute(self, stop_event : asyncio.Event):

        if self.parsed_url.scheme == "tcp":
            return await self.__main_tcp(stop_event)

        elif self.parsed_url.scheme == "unix":
            return await self.__main_unix(stop_event)

        else:
            self.log.info("Invalid SERVER_TYPE. Choose 'TCP' or 'UNIX'.")


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
        raise ExceptZen(f"scheme {parsed_url.scheme} invalid")
