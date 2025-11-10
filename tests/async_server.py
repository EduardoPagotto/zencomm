#!/usr/bin/env python3
'''
Created on 20241001
Update on 20251031
@author: Eduardo Pagotto
'''

import asyncio

import os
import sys
sys.path.append(os.path.join(os.getcwd(), './src'))

from zencomm.header import ProtocolCode
from zencomm.asy import get_async_logger
from zencomm.asy.protocol import Protocol
from zencomm.asy.socket import SocketServer

URL = 'unix:///tmp/teste0.sock'

logger = get_async_logger('zen')

async def handle_client(reader, writer):

    logger.info("connection start")

    p = Protocol(reader, writer)

    try:

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
                raise Exception(f"codigo invalido: {code}")

    except Exception as exp:
        logger.error(f"connection fail: {str(exp)}")

    logger.info("connection stop")


async def main():
    await logger.info("server start.")

    server = SocketServer(URL,handle_client)

    await server.execute()

    await logger.info("server stop.")
    await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
