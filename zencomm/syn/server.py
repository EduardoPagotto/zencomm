#!/usr/bin/env python3
'''
Created on 20190822
Update on 20251111
@author: Eduardo Pagotto
'''

from socket import socket, timeout
import logging
import threading

from datetime import datetime, timezone, timedelta
from typing import Any, List

class ServiceServer(threading.Thread):
    """[Class facture new connections threads]
    Args:
        object ([type]): [description]
    """
    def __init__(self, sock : socket, responser : Any):
        """[Initialize with socket and responser]
        Args:
            sock (socket.socket): [description]
            responser (RPC_Responser): [description]
        """
        threading.Thread.__init__(self, name='factory_conn')

        self.sock = sock
        self.responser = responser

        self.lista : List[threading.Thread]= []

        self.done : bool = False
        self.stop_event = threading.Event()

        self.log = logging.getLogger(__name__)

        self.total = 0
        self.anterior = 0
        self.startApp = datetime.timestamp(datetime.now(tz=timezone.utc))


    def stop(self) -> None:
        """[Signal to stop server]
        """
        self.log.info('Factory connections signal to stop')
        self.stop_event.set()
        self.sock.close()
        self.done = True

    def garbage(self) -> None:
        """[Thread to remove connections deads]
        """
        lista_remover = []
        for th in self.lista:
            if th.is_alive() is False:
                th.join()
                lista_remover.append(th)

        for th in lista_remover:
            self.log.debug('Thread removed %s', th.getName())
            self.lista.remove(th)

        removed = len(lista_remover)
        if removed > 0:
            self.total += removed
            lista_remover.clear()

        atual = len(self.lista)
        if (atual != self.anterior) or (removed > 0):
            self.anterior = atual

            time_online = int(datetime.timestamp(datetime.now(tz=timezone.utc)) - self.startApp)
            self.log.info('alive[%s] run[%d] sweeped[%d]', str(timedelta(seconds=time_online)), atual, self.total)

    def run(self):
        """[Thread factory of new connectons to client]
        """
        self.log.info("Factory connections start")
        seq = 0
        while self.done is False:
            try:
                # accept connections from outside
                clientsocket, address = self.sock.accept()
                t = threading.Thread(target=self.responser, name='tResp_{0}'.format(seq), args=(clientsocket,
                                                                                                address,
                                                                                                self.stop_event,))
                t.start()
                self.lista.append(t)
                seq += 1

            except timeout:
                self.log.info('to')

            except Exception as exp:
                if self.done is False:
                    self.log.error('Fail:%s', str(exp))

        self.log.info("Factory connection stop")
