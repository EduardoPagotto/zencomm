'''
Created on 20251107
Update on 20251112
@author: Eduardo Pagotto
'''

import os

from zencomm import ExceptZen
from socket import socket, AF_INET, AF_UNIX, SOCK_STREAM
from urllib.parse import urlparse

def socket_server(parsed_url: urlparse, timeout : float, listen_val: int) -> socket: # pyright: ignore[reportGeneralTypeIssues]

    soc = None
    if parsed_url.scheme == "tcp":

        host = parsed_url.hostname
        port = parsed_url.port

        soc = socket(AF_INET, SOCK_STREAM)
        soc.settimeout(timeout)

        # TODO: get by hostname
        #soc.bind((soc.getSocket().gethostname(), porta))
        soc.bind((host, port))

    elif parsed_url.scheme == "unix":

        path = parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}'

        if os.path.exists(path):
            os.remove(path)

        soc = socket(AF_UNIX, SOCK_STREAM)
        soc.settimeout(timeout)
        soc.bind(path)

    else:
        raise ExceptZen(f"scheme {parsed_url.scheme} invalid")

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
        soc = socket(AF_UNIX, SOCK_STREAM)
        soc.settimeout(float(timeout))
        soc.connect((host, port))

    elif parsed_url.scheme == "unix":

        path = parsed_url.path if not parsed_url.hostname else f'.{parsed_url.path}'

        soc = socket(AF_UNIX, SOCK_STREAM)
        soc.settimeout(float(timeout))
        soc.connect(path)

    else:
        raise ExceptZen(f"scheme {parsed_url.scheme} invalid")

    return soc
