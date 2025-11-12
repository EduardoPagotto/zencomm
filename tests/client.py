#!/usr/bin/env python3
'''
Created on 20170119
Update on 20251112
@author: Eduardo Pagotto
'''

import logging
import time
from urllib.parse import urlparse

import os
import sys
sys.path.append(os.path.join(os.getcwd(), '.'))

from zencomm import ProtocolCode, setup_queue_logging
from zencomm.syn import Protocol, socket_client

logger_listern = setup_queue_logging('./log/client.log')
logger = logging.getLogger('client')

def main():

    try:

        url_parser = urlparse('unix:///tmp/teste0.sock')

        sock = socket_client(url_parser, 10)

        protocol = Protocol(sock)
        #logger.info(protocol.handShake())

        protocol.sendString(ProtocolCode.COMMAND, 'ola 123')

        idval, msg = protocol.receiveString()
        logger.info('Recebido id:%s msg:%s', str(idval), msg)

        time.sleep(30)

        # protocol.sendString(ProtocolCode.ERRO, 'Erro Critico')
        # idVal, msg = protocol.receiveString()
        # logger.info('Recebido id:%s msg:%s', idVal, msg)

        protocol.sendClose('Bye-Bye')

        logger.info('Desconectado')

    except Exception as exp:
        logger.exception('Falha %s', str(exp))

    logger.info('App desconectado')



if __name__ == '__main__':
    main()
