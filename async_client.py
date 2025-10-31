#!/usr/bin/env python3
'''
Created on 20251030
Update on 20251030
@author: Eduardo Pagotto
'''

import asyncio
from urllib.parse import urlparse

from zen import get_async_logger
from zen.protocol import Protocol, ProtocolCode

URL = 'unix:///tmp/teste0.sock'

logger = get_async_logger('zen')

async def create_client_connection(parsed_url : urlparse) -> tuple[any]:

    timeout = 60

    if parsed_url.scheme == "tcp":

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host=parsed_url.hostname, port=parsed_url.port),
                timeout=timeout
            )

            return reader, writer
            #writer.close()
            #await writer.wait_closed()
        except asyncio.TimeoutError:
            logger.error(f"Connection to {parsed_url.hostname}:{parsed_url.port} timed out after {timeout} seconds.")
            return None, None
        except OSError as e:
            logger.error(f"Error connecting to {parsed_url.hostname}:{parsed_url.port}: {e}")
            return None, None


    elif parsed_url.scheme == "unix":

        final = parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}'

        try:

            reader, writer = await asyncio.wait_for(
                asyncio.open_unix_connection(path=final),
                timeout=timeout
            )

            return reader, writer

        except asyncio.TimeoutError:
            logger.error(f"Connection to {final} timed out after {timeout} seconds.")
            return None, None

        except FileNotFoundError:
            logger.error(f"Unix socket not found at {final}")
            return None, None

        except ConnectionRefusedError:
            logger.error(f"Connection to {final} refused.")
            return None, None

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None, None

async def main():

    await logger.info("client start.")

    reader, writer = await create_client_connection(urlparse(URL))

    if reader and writer:

        p = Protocol(reader, writer)

        await p.sendString(ProtocolCode.COMMAND, 'teste 123....')
        c, m = await p.receiveString()
        logger.info(f'Retorno: {m}')

        await p.sendString(ProtocolCode.COMMAND, 'MSG FINAL!!!!!!!!!!!')
        await asyncio.sleep(30)
        await p.sendClose('fim!')

        # writer.close()
        # await writer.wait_closed()

    await logger.info("client stop.")
    await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
