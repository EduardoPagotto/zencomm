#!/usr/bin/env python3
'''
Created on 20241001
Update on 20251108
@author: Eduardo Pagotto
'''

import asyncio

import os
import sys
sys.path.append('.')
sys.path.append(os.path.join(os.getcwd(), 'zen'))

from zen.asynchronous import get_async_logger
from zen.asynchronous.socket import SocketServer
from zen.asynchronous.rpc.responser import Responser

URL = 'unix:///tmp/teste0.sock'

logger = get_async_logger('zen')

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
