'''
Created on 20241001
Update on 20251030
@author: Eduardo Pagotto
'''

import logging
import os
from urllib.parse import urlparse

import asyncio

class SocketServer(object):
    def __init__(self, url):
        self.url = url
        self.log = logging.getLogger('Zero')

    async def entry_point(self, func, *args, **kwargs):
        await func(*args, **kwargs)

    async def __handle_client(self, reader, writer):
        await self.entry_point(reader=reader, writer=writer)

    async def __main_tcp(self, host, port):
        """
        Starts an asyncio TCP server.
        """
        server = await asyncio.start_server(self.__handle_client, host, port)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        self.log.info(f"Serving on {addrs}")

        async with server:
            await server.serve_forever()

    async def __main_uds(self, path):
        """
        Starts an asyncio Unix Domain Socket server.
        """
        if os.path.exists(path):
            os.remove(path)  # Clean up previous socket file if it exists

        server = await asyncio.start_unix_server(self.__handle_client, path)
        self.log.info(f"Serving on UDS: {path}")

        async with server:
            await server.serve_forever()

    async def create_socket(self):

        parsed_url = urlparse(self.url)

        if parsed_url.scheme == "tcp":
            asyncio.run(self.__main_tcp(parsed_url.hostname, parsed_url.port))

        elif parsed_url.scheme == "uds":
            asyncio.run(self.__main_uds(parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}'))

        else:
            self.log.info("Invalid SERVER_TYPE. Choose 'TCP' or 'UDS'.")


async def create_client_connection(url : str) -> tuple[any]:

    parsed_url = urlparse(url)

    if parsed_url.scheme == "tcp":
        return  await asyncio.open_connection(host=parsed_url.hostname, port=parsed_url.port)

    elif parsed_url.scheme == "uds":
        return await asyncio.open_unix_connection(parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}')

    else:
        raise Exception("Falha de conexao")
