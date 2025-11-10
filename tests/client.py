#!/usr/bin/env python3
'''
Created on 20170119
Update on 20251108
@author: Eduardo Pagotto
'''

import logging
import time
from urllib.parse import urlparse

import os
import sys
sys.path.append(os.path.join(os.getcwd(), './src'))

from zencomm.header import ProtocolCode
from zencomm.syn.protocol import Protocol
from zencomm.syn.socket import socket_client


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(threadName)-16s %(funcName)-20s %(message)s',
    datefmt='%H:%M:%S',
)

def main():

    log = logging.getLogger('Client')

    try:

        url_parser = urlparse('unix:///tmp/teste0.sock')

        sock = socket_client(url_parser, 10)

        protocol = Protocol(sock)
        #log.info(protocol.handShake())

        protocol.sendString(ProtocolCode.COMMAND, 'ola 123')

        idval, msg = protocol.receiveString()
        log.info('Recebido id:%s msg:%s', str(idval), msg)

        time.sleep(30)

        # protocol.sendString(ProtocolCode.ERRO, 'Erro Critico')
        # idVal, msg = protocol.receiveString()
        # log.info('Recebido id:%s msg:%s', idVal, msg)

        protocol.sendClose('Bye-Bye')

        log.info('Desconectado')

    except Exception as exp:
        log.exception('Falha %s', str(exp))

    log.info('App desconectado')



if __name__ == '__main__':
    main()
