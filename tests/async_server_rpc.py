#!/usr/bin/env python3
'''
Created on 20241001
Update on 20251111
@author: Eduardo Pagotto
'''

import asyncio
import json
import os
import socket
import sys
import threading

from sjsonrpc.asy import RPC_Responser

sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm.asy.protocol import Protocol
from zencomm.header import ProtocolCode
from zencomm.asy import get_async_logger
from zencomm.asy.socket import SocketServer

URL = 'unix:///tmp/teste0.sock'

logger = get_async_logger('zen')

class Responser(RPC_Responser):
    def __init__(self, target: object):
        super().__init__(target)

    async def __call__(self, *args, **kargs):
        """[execute exchange of json's messages with server RPC]
        """
        t_name = threading.current_thread().name
        logger.info(f'start {t_name}')

        protocol = None
        try:
            protocol = Protocol(args[0], args[1])

        except Exception as exp:
            await logger.critical('fail creating connection: %s', str(exp))
            return

        count_to = 0

        while True:
            try:
                count_to = 0
                idRec, buffer = await protocol._receiveProtocol()
                if idRec == ProtocolCode.COMMAND:
                    await protocol.sendString(ProtocolCode.RESULT, json.dumps(await self.encode_exec_decode(json.loads(buffer.decode('UTF-8')))))

                elif idRec == ProtocolCode.CLOSE:
                    logger.debug(f'responser receive {buffer.decode('UTF-8')}')
                    break

            except socket.timeout:
                count_to += 1
                logger.warning('%s TO count: %d', t_name, count_to)

            except Exception as exp:
                logger.error('%s exception error: %s', t_name, str(exp))
                break

        await protocol.close()

        await logger.info(f'{t_name} finnished')


class ServerRPC(object):
    def __init__(self, url: str):
        self.server = SocketServer(url, Responser(self))
        self.nome = ''

    async def execute(self):
        await self.server.execute()

    async def set_nome(self, nome: str):
        self.nome = nome

    async def get_nome(self):
        return self.nome

    async def teste(self, nome):
        await logger.info(f"Methodo TESTE recebido com {nome}")
        return "MSG_RECEBIDA_OK!!!!"


async def main():
    await logger.info("server start.")

    server = ServerRPC(URL)
    await server.execute()

    await logger.info("server stop.")
    await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
