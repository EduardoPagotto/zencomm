#!/usr/bin/env python3
'''
Created on 20241001
Update on 20251114
@author: Eduardo Pagotto
'''

import asyncio
import logging
import os
import signal
import sys
sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm import ProtocolCode, setup_queue_logging
from zencomm.asy import Protocol, SocketServer

logger_listern = setup_queue_logging('./log/async_server.log')
logger = logging.getLogger('async_server')

async def handle_client(stop_event, reader, writer):

    logger.info("connection start")

    p = Protocol(reader, writer, 5)
    to_count = 0

    while not stop_event.is_set():
        try:
            code, msg = await p.receiveString()
            if code == ProtocolCode.CLOSE:
                logger.info(f"close recebido: {msg}")
                break

            elif code == ProtocolCode.COMMAND:
                logger.info(f"msg recebida: {msg}")
                await p.sendString(ProtocolCode.RESULT, "Recebido OK!!!")
            else:
                raise Exception(f"codigo invalido: {code}")

        except asyncio.TimeoutError:
            to_count += 1
            logger.warning(f"timeout receiving: {to_count}")

        except asyncio.IncompleteReadError as ein:
            logger.error(f"incomplete read: {str(ein)}")
            break
        except Exception as exp:
            logger.error(f"comm fail: {str(exp)}")
            break


    logger.info("connection stop")


async def main():
    logger.info("server start.")

    # Set up a signal handler for graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        #self.log.warning("Shutdown signal received...")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    server = SocketServer('unix:///tmp/teste0.sock', handle_client, stop_event)

    await server.execute()

    logger.info("server stop.")

if __name__ == "__main__":
    asyncio.run(main())
