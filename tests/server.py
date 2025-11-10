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

import os
import sys
sys.path.append(os.path.join(os.getcwd(), './src'))

from zencomm.utils import GracefulKiller
from zencomm.syn.protocol import Protocol, ProtocolCode
from zencomm.syn.server import ServiceServer
from zencomm.syn.socket import socket_server

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(threadName)-16s %(funcName)-20s %(message)s',
    datefmt='%H:%M:%S',
)

def connection(sock, addr, stop_event):

    log = logging.getLogger('Zero.Con')

    log.info('connection stated')

    #done = kwargs['done']
    protocol = None
    try:
        protocol = Protocol(sock)
        protocol.sock.settimeout(2)

    except Exception as exp:
        log.exception('falha na parametrizacao da conexao: {0}'.format(str(exp)))
        return

    while not stop_event.is_set():
        try:
            idRec, msg = protocol.receiveString()
            if idRec == ProtocolCode.COMMAND:

                log.debug('Comando Recebido:{0}'.format(msg))
                protocol.sendString(ProtocolCode.RESULT, 'echo: {0}'.format(msg))

            elif idRec == ProtocolCode.CLOSE:
                log.debug(f"close recebido: {msg}")
                break

        except timeout:
            log.debug('timeout receive')

        except Exception as exp:
            log.error('error: {0}'.format(str(exp)))
            break


    log.info('connection finished')

def main():

    url_parser = urlparse('unix:///tmp/teste0.sock')

    sock = socket_server(url_parser, 10.0, 15) # to aqui é de espera de conexao

    killer = GracefulKiller()

    log = logging.getLogger('Server')
    logging.getLogger('Zero').setLevel(logging.INFO)


    log.debug('server timeout: %s', str(sock.gettimeout()))

    service = ServiceServer(sock, connection)
    service.start()

    cycle = 0
    while not service.done:

        log.info('cycle:%d connections:%d', cycle, len(service.lista))
        cycle += 1
        time.sleep(5)

        service.garbage()

        if killer.kill_now is True:
            sock.close()
            service.stop()
            break

    service.join()

if __name__ == '__main__':
    main()
