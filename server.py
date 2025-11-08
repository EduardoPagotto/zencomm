#!/usr/bin/env python3
'''
Created on 20170119
Update on 20220921
@author: Eduardo Pagotto
'''

import time
import logging
from socket import timeout
from urllib.parse import urlparse

#import common

from zen.utils import GracefulKiller
from zen.syncronos.protocol import Protocol, ProtocolCode
from zen.syncronos.server import ServiceServer
from zen.syncronos.socket import socket_server

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
        protocol.sock.settimeout(10)

    except Exception as exp:
        log.exception('falha na parametrizacao da conexao: {0}'.format(str(exp)))
        return

    while not stop_event.is_set():
        try:
            idRec, msg = protocol.receiveString()
            if idRec is ProtocolCode.COMMAND:

                # comando_str = msg.replace("'", "\"")
                # comando_dic = json.loads(comando_str)
                # comando = comando_dic['comando']

                log.debug('Comando Recebido:{0}'.format(msg))

                if msg == 'ola 123':
                    protocol.sendString(ProtocolCode.RESULT, 'echo: {0}'.format(msg))
                else:
                    protocol.sendString(ProtocolCode.RESULT, 'teste 2')

        # except ExceptionZeroErro as exp_erro:
        #     log.warning('recevice Erro: {0}'.format(str(exp_erro)))
        #     protocol.sendString(ProtocolCode.RESULT, 'recived error from server')

        # except ExceptionZeroClose as exp_close:
        #     log.debug('receive Close: {0}'.format(str(exp_close)))
        #     break

        except timeout:
            log.debug('connection timeout..')

        except Exception as exp:
            log.error('error: {0}'.format(str(exp)))
            break


    log.info('connection finished')

def main():

    url_parser = urlparse('unix:///tmp/teste0.sock')

    sock = socket_server(url_parser, 300.0, 15)

    killer = GracefulKiller()

    log = logging.getLogger('Server')
    logging.getLogger('Zero').setLevel(logging.INFO)


    log.debug('server timeout: %s', str(sock.gettimeout()))

    service = ServiceServer(sock, connection)

    service.start()

    cycle = 0
    while True:

        log.info('cycle:%d connections:%d', cycle, len(service.lista))
        cycle += 1
        time.sleep(5)

        if killer.kill_now is True:
            sock.close()
            service.stop()
            break

    service.join()

if __name__ == '__main__':
    main()
