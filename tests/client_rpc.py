#!/usr/bin/env python3
'''
Created on 20170119
Update on 20251108
@author: Eduardo Pagotto
'''

import json
from typing import Any
from urllib.parse import urlparse

import os
import sys
sys.path.append(os.path.join(os.getcwd(), './src'))

from zencomm.header import ProtocolCode
from zencomm.syn import get_logger
from zencomm.syn.protocol import Protocol
from zencomm.syn.socket import socket_client
from zencomm.syn.rpc.ConnectionControl import ConnectionControl
from zencomm.syn.rpc.ProxyObject import ProxyObject

logger = get_logger('zen_client')

class ConnectionRemote(ConnectionControl):
    def __init__(self, url):
        super().__init__(url)

    def exec(self, input_rpc : dict, *args, **kargs) -> dict:

        timeout = 60
        url = self.getUrl()
        parsed_url = urlparse(url)

        result : dict = {}

        try:
            soc = socket_client(parsed_url, timeout)
            if soc:
                p = Protocol(soc)

                payload = json.dumps(input_rpc)

                p.sendString(ProtocolCode.COMMAND, payload)
                c, m = p.receiveString()
                if c == ProtocolCode.RESULT:
                    result = json.loads(m)
                else:
                    raise Exception(m)

                p.sendClose('bye')

        except FileNotFoundError:
            logger.error(f"Unix socket not found at {parsed_url.geturl()}")

        except ConnectionRefusedError:
            logger.error(f"Connection to {parsed_url.geturl()} refused.")

        except ConnectionResetError:
            logger.error(f"Client {parsed_url.geturl()} forcibly closed the connection.")

        except BrokenPipeError as eb:
            logger.error(f"Connection is dead: {str(eb)}")

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")

        finally:
            logger.info("client stop.")

        return result

class ClientRCP(object):
    def __init__(self, addr) -> None:
        self.comm = ConnectionRemote(addr)

    def __rpc(self) -> Any:
        return ProxyObject(self.comm)

    def teste(self, nome : str) -> str:
        return self.__rpc().teste(nome)


def main():

    try:

        client = ClientRCP('unix:///tmp/teste0.sock')

        val = client.teste("estuardo")
        logger.info(f"Recebido {val}")


    except Exception as exp:
        logger.exception('Falha %s', str(exp))

    logger.info('App desconectado')



if __name__ == '__main__':
    main()
