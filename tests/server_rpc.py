#!/usr/bin/env python3
'''
Created on 20170119
Update on 20251111
@author: Eduardo Pagotto
'''

import json
import socket
import threading
import time
from urllib.parse import urlparse

from sjsonrpc.syn import RPC_Responser

import os
import sys
sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm.header import ProtocolCode
from zencomm.syn.protocol import Protocol
from zencomm.utils import GracefulKiller
from zencomm.syn import get_logger
from zencomm.syn.server import ServiceServer
from zencomm.syn.socket import socket_server

logger = get_logger('zen')

class Responser(RPC_Responser):
    def __init__(self, target: object):
        super().__init__(target)

    def __call__(self, *args, **kargs):
        """[execute exchange of json's messages with server RPC]
        """

        t_name = threading.current_thread().name
        logger.info(f'start {t_name}')

        protocol = None
        try:
            protocol = Protocol(args[0])

        except Exception as exp:
            logger.critical('fail creating connection: %s', str(exp))
            return

        count_to = 0

        while True:
            try:
                count_to = 0
                idRec, buffer = protocol._receiveProtocol()
                if idRec == ProtocolCode.COMMAND:
                    protocol.sendString(ProtocolCode.RESULT, json.dumps(self.encode_exec_decode(json.loads(buffer.decode('UTF-8')))))

                elif idRec == ProtocolCode.CLOSE:
                    logger.debug(f'responser receive {buffer.decode('UTF-8')}')
                    break

            except socket.timeout:
                count_to += 1
                logger.warning('%s TO count: %d', t_name, count_to)

            except Exception as exp:
                logger.error('%s exception error: %s', t_name, str(exp))
                break

        protocol.close()

        logger.info(f'{t_name} finnished')

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
