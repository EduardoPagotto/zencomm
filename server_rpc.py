#!/usr/bin/env python3
'''
Created on 20170119
Update on 20251108
@author: Eduardo Pagotto
'''

import time
import logging
from socket import timeout
from urllib.parse import urlparse

from zen.utils import GracefulKiller
from zen.syncronos import get_logger

from zen.syncronos.rpc.responser import Responser
from zen.syncronos.server import ServiceServer
from zen.syncronos.socket import socket_server

logger = get_logger('zen')

class ServerRPC(object):
    def __init__(self, url: str):

        url_parser = urlparse(url)
        sock = socket_server(url_parser, 10.0, 15) # to aqui é de espera de conexao

        self.killer = GracefulKiller()
        self.service = ServiceServer(sock, Responser(self))
        self.service.start()

    def execute(self):
        cycle = 0
        while not self.service.done:

            logger.info('cycle:%d connections:%d', cycle, len(self.service.lista))
            cycle += 1
            time.sleep(5)

            self.service.garbage()

            if self.killer.kill_now is True:
                self.service.sock.close()
                self.service.stop()
                break

        self.service.join()


    def set_nome(self, nome: str):
        self.nome = nome

    def get_nome(self):
        return self.nome

    def teste(self, nome):
        logger.info(f"Methodo TESTE recebido com {nome}")
        return "MSG_RECEBIDA_OK!!!!"


def main():

    server = ServerRPC('unix:///tmp/teste0.sock')
    server.execute()

if __name__ == '__main__':
    main()
