#!/usr/bin/env python3
'''
Created on 20241001
Update on 20251031
@author: Eduardo Pagotto
'''

import asyncio

from zen.asynchronous.rpc.responser import Responser
from zen.header import ProtocolCode
from zen.asynchronous import get_async_logger
from zen.asynchronous.protocol import Protocol
from zen.asynchronous.socket import SocketServer

URL = 'unix:///tmp/teste0.sock'

logger = get_async_logger('zen')

class ServerRPC(object):
    def __init__(self, url : str, target : object):
        self.server = SocketServer(url, Responser(target))

    async def execute(self):
        await self.server.execute()


class ServerGeneric(ServerRPC):
    def __init__(self, url: str):
        super().__init__(url, self)
        self.nome = ''

    async def set_nome(self, nome: str):
        self.nome = nome

    async def get_nome(self):
        return self.nome

    async def teste(self, nome):
        await logger.info(f"Methodo TESTE recebido com {nome}")
        return "MSG_RECEBIDA_OK!!!!"


async def main():
    await logger.info("server start.")

    server = ServerGeneric(URL)
    await server.execute()

    #server = SocketServer(URL,handle_client)
    #await server.execute()

    await logger.info("server stop.")
    await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
