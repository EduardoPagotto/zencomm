#!/usr/bin/env python3
'''
Created on 20251030
Update on 20251111
@author: Eduardo Pagotto
'''

import asyncio
from urllib.parse import urlparse

import os
import sys
sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm.header import ProtocolCode
from zencomm.asy.logger import get_async_logger
from zencomm.asy import Protocol, socket_client

URL = 'unix:///tmp/teste0.sock'

logger = get_async_logger('zen')


async def main():

    await logger.info("client start.")

    timeout = 60
    parsed_url = urlparse(URL)

    try:
        reader, writer = await socket_client(parsed_url, timeout)
        if reader and writer:

                p = Protocol(reader, writer)

                await p.sendString(ProtocolCode.COMMAND, 'cliente envia: teste 123....')
                c, m = await p.receiveString()
                await logger.info(f'Retorno servidor: {m}')

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
        await logger.info("client stop.")

    await logger.shutdown()


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Client shutting down gracefully...")
    except asyncio.CancelledError:
        print("Client task cancelled gracefully...")
