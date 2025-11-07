'''
Created on 20251107
Update on 20251107
@author: Eduardo Pagotto
'''

import logging
import os
import socket

import sys
from urllib.parse import urlparse

class SocketServer(object):
    def __init__(self, url : str, timeout : float):
        self.parsed_url = urlparse(url)
        self.timeout = timeout
        self.log = logging.getLogger('zen')

    def __main_tcp(self):
        host = self.parsed_url.hostname
        port = self.parsed_url.port

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.settimeout(self.timeout)

        # TODO: get by hostname
        #soc.bind((soc.getSocket().gethostname(), porta))
        soc.bind((host, port))

        return soc


    def __main_unix(self):
        path = self.parsed_url.path if not self.parsed_url.hostname else f'.{self.parsed_url.path}'

        if os.path.exists(path):
            os.remove(path)

        soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        soc.settimeout(self.timeout)
        soc.bind(path)

        return soc

    def create(self, listen_val: int) :

        soc = None
        if self.parsed_url.scheme == "tcp":
            soc = self.__main_tcp()
        elif self.parsed_url.scheme == "unix":
            soc = self.__main_unix()
        else:
            self.log.info("Invalid SERVER_TYPE. Choose 'TCP' or 'UNIX'.")
            return None

        soc.listen(listen_val)

        return soc

    # # TODO: implementar a continuação do inetd,
    # # neste caso a conexao ja é a final, indo direto para o protocolo
    # def inetd_conn(self):
    #     soc = socket.fromfd(sys.stdin.fileno(), socket.AF_INET, socket.SOCK_STREAM)
    #     server_address = soc.getsockname()
    #     self.log.debug('Connected in: %s', str(server_address))

    #     return soc


def socket_client(parsed_url : urlparse, timeout : int): # pyright: ignore[reportGeneralTypeIssues]

    soc = None
    if parsed_url.scheme == "tcp":
        host = parsed_url.hostname
        port = parsed_url.port
        soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        soc.settimeout(float(timeout))
        soc.connect((host, port))

    elif parsed_url.scheme == "unix":

        path = parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}'

        soc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        soc.settimeout(float(timeout))
        soc.connect(path)

    else:
        raise Exception(f"scheme {parsed_url.scheme} invalid")

    return soc
