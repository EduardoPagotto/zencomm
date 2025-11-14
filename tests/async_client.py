#!/usr/bin/env python3
'''
Created on 20251030
Update on 20251114
@author: Eduardo Pagotto
'''

import os
import sys
import asyncio
import logging
from urllib.parse import urlparse

sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm.header import ProtocolCode
from zencomm.logger import setup_queue_logging
from zencomm.asy import Protocol, socket_client

logger_listern = setup_queue_logging('./log/async_client.log')
logger = logging.getLogger('async_client')

async def main():

    logger.info("client start.")

    timeout = 60
    parsed_url = urlparse('unix:///tmp/teste0.sock')

    try:
        reader, writer = await socket_client(parsed_url, timeout)
        if reader and writer:

                p = Protocol(reader, writer, 30)

                await p.sendString(ProtocolCode.COMMAND, 'cliente envia: teste 123....')
                c, m = await p.receiveString()
                logger.info(f'Retorno servidor: {m}')

                #await p.sendString(ProtocolCode.COMMAND, 'MSG FINAL!!!!!!!!!!!')
                await asyncio.sleep(30)
                await p.sendClose('fim!')

    except asyncio.TimeoutError:
        logger.error(f"Connection to {parsed_url.geturl()} timed out after {timeout} seconds.")

    except FileNotFoundError:
        logger.error(f"Unix socket not found at {parsed_url.geturl()}")

    except ConnectionRefusedError:
        logger.error(f"Connection to {parsed_url.geturl()} refused.")

    except asyncio.IncompleteReadError:
        logger.error(f"Client {parsed_url.geturl()} disconnected unexpectedly.")

    except ConnectionResetError:
        logger.error(f"Client {parsed_url.geturl()} forcibly closed the connection.")

    # except asyncio.CancelledError:
    #     logger.error("Client task cancelled gracefully..")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

    finally:
        logger.info("client stop.")


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Client shutting down gracefully...")
    except asyncio.CancelledError:
        logger.info("Client task cancelled gracefully...")
