#!/usr/bin/env python3
'''
Created on 20241001
Update on 20251030
@author: Eduardo Pagotto
'''

import os
import asyncio
from urllib.parse import urlparse

from zen import get_async_logger
from zen.protocol import Protocol, ProtocolCode

URL = 'unix:///tmp/teste0.sock'

logger = get_async_logger('zen')

async def handle_client(reader, writer):

    logger.info("connection start")

    p = Protocol(reader, writer)

    is_online = True
    while is_online:

        code, msg = await p.receiveString()
        if code == ProtocolCode.CLOSE:
            await logger.info(f"close recebido: {msg}")
            is_online = False

        elif code == ProtocolCode.COMMAND:
            await logger.info(f"msg recebida: {msg}")
            await p.sendString(ProtocolCode.RESULT, "Recebido OK!!!")

        else:
            raise Exception(f"Codigo invalido: {code}")

    logger.info("connection stop")

async def main_tcp(parsed_url : urlparse):
    """
    Starts an asyncio TCP server.
    """

    host = parsed_url.hostname
    port = parsed_url.port

    server = await asyncio.start_server(handle_client, host, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)

    await logger.info(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()

async def main_unix(parsed_url : urlparse):
    """
    Starts an asyncio Unix Domain Socket server.
    """

    path = parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}'

    if os.path.exists(path):
        os.remove(path)

    server = await asyncio.start_unix_server(handle_client, path)

    await logger.info(f"Serving on {parsed_url.geturl()}")

    async with server:
        await server.serve_forever()


async def execute_server(parsed_url : urlparse):

    if parsed_url.scheme == "tcp":
        return await main_tcp(parsed_url)

    elif parsed_url.scheme == "unix":
        return await main_unix(parsed_url)

    else:
        logger.info("Invalid SERVER_TYPE. Choose 'TCP' or 'UNIX'.")


async def main():
    await logger.info("server start.")

    await execute_server(urlparse(URL))

    await logger.info("server stop.")
    await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
