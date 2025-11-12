#!/usr/bin/env python3
'''
Created on 20241001
Update on 20251112
@author: Eduardo Pagotto
'''

import asyncio
import logging
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm import ProtocolCode, setup_queue_logging
from zencomm.asy import Protocol, SocketServer

logger_listern = setup_queue_logging('./log/async_server.log')
logger = logging.getLogger('async_server')

async def handle_client(reader, writer):

    logger.info("connection start")

    p = Protocol(reader, writer)

    try:

        is_online = True
        while is_online:

            code, msg = await p.receiveString()
            if code == ProtocolCode.CLOSE:
                logger.info(f"close recebido: {msg}")
                is_online = False

            elif code == ProtocolCode.COMMAND:
                logger.info(f"msg recebida: {msg}")
                await p.sendString(ProtocolCode.RESULT, "Recebido OK!!!")

            else:
                raise Exception(f"codigo invalido: {code}")

    except Exception as exp:
        logger.error(f"connection fail: {str(exp)}")

    logger.info("connection stop")


async def main():
    logger.info("server start.")

    server = SocketServer('unix:///tmp/teste0.sock', handle_client)
    await server.execute()

    logger.info("server stop.")

if __name__ == "__main__":
    asyncio.run(main())
