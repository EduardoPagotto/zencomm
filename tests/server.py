#!/usr/bin/env python3
'''
Created on 20170119
Update on 20251112
@author: Eduardo Pagotto
'''

import time
import logging
from socket import timeout
from urllib.parse import urlparse

import os
import sys
sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm import ProtocolCode, GracefulKiller
from zencomm.syn import Protocol, ServiceServer, socket_server
from zencomm import setup_queue_logging

logger_listern = setup_queue_logging('./log/server.log')
logger = logging.getLogger('server')

def connection(sock, addr, stop_event):

    logger.info('connection stated')

    #done = kwargs['done']
    protocol = None
    try:
        protocol = Protocol(sock)
        protocol.sock.settimeout(2)

    except Exception as exp:
        logger.exception('falha na parametrizacao da conexao: {0}'.format(str(exp)))
        return

    while not stop_event.is_set():
        try:
            idRec, msg = protocol.receiveString()
            if idRec == ProtocolCode.COMMAND:

                logger.debug('Comando Recebido:{0}'.format(msg))
                protocol.sendString(ProtocolCode.RESULT, 'echo: {0}'.format(msg))

            elif idRec == ProtocolCode.CLOSE:
                logger.debug(f"close recebido: {msg}")
                break

        except timeout:
            logger.debug('timeout receive')

        except Exception as exp:
            logger.error('error: {0}'.format(str(exp)))
            break


    logger.info('connection finished')

def main():

    url_parser = urlparse('unix:///tmp/teste0.sock')

    sock = socket_server(url_parser, 10.0, 15) # to aqui é de espera de conexao

    killer = GracefulKiller()

    logger.debug('server timeout: %s', str(sock.gettimeout()))

    service = ServiceServer(sock, connection)
    service.start()

    cycle = 0
    while not service.done:

        logger.info('cycle:%d connections:%d', cycle, len(service.lista))
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
