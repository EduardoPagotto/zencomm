'''
Created on 20190824
Update on 20251108
@author: Eduardo Pagotto
'''

import socket
import json
import threading

from zencomm import ExceptZen, __json_rpc_version__ as json_rpc_version

from zencomm.syn import get_logger
from zencomm.syn.protocol import Protocol
from zencomm.header import ProtocolCode

class Responser(object):
    """[Connection thread with server RPC ]
    Args:
        object ([type]): [description]
    """

    def __init__(self, target : object):
        """[summary]
        Args:
            target (object): [Method Name to run in RPC Server]
        """
        self.log = get_logger()
        self.target : object= target

    def __call__(self, *args, **kargs):
        """[execute exchange of json's messages with server RPC]
        """

        t_name = threading.current_thread().name
        self.log.info(f'start {t_name}')

        protocol = None
        try:
            protocol = Protocol(args[0])

        except Exception as exp:
            self.log.critical('fail creating connection: %s', str(exp))
            return

        count_to = 0

        while True:
            try:
                count_to = 0
                idRec, buffer = protocol._receiveProtocol()
                if idRec == ProtocolCode.COMMAND:
                    protocol.sendString(ProtocolCode.RESULT, self.rpc_exec_func(buffer.decode('UTF-8'), protocol))

                elif idRec == ProtocolCode.CLOSE:
                    self.log.debug(f'responser receive {buffer.decode('UTF-8')}')
                    break

            except socket.timeout:
                count_to += 1
                self.log.warning('%s TO count: %d', t_name, count_to)

            except Exception as exp:
                self.log.error('%s exception error: %s', t_name, str(exp))
                break

        protocol.close()

        self.log.info(f'{t_name} finnished')

    def rpc_exec_func(self, msg : str, protocol : Protocol) -> str:
        """[Execule methodo local with paramters in json data (msg)]
        Args:
            msg (str): [json Protocol data received (id, method, parameters)]
        Returns:
            str: [Resulto of method in json Protocol]
        """

        try:

            dados : dict = json.loads(msg)
            serial : int = dados['id']
            metodo : str = dados['method']

        except Exception as exp3:
            return json.dumps({'jsonrpc': json_rpc_version, 'error': {'code': -32603, 'message': 'Not json: ' + str(exp3)}, 'id': 0})

        try:
            val = getattr(self.target, metodo)(*dados['params'], **dados['keys'])
            return json.dumps({'jsonrpc': json_rpc_version, 'result': val, 'id': serial})

        except AttributeError as exp:
            return json.dumps({'jsonrpc': json_rpc_version, 'error': {'code': -32601, 'message': 'Method not found: '+ str(exp)}, 'id': serial})

        except TypeError as exp1:
            return json.dumps({'jsonrpc': json_rpc_version, 'error': {'code': -32602, 'message': 'Invalid params: '+ str(exp1)}, 'id': serial})

        except ExceptZen as exp2:
            tot = len(exp2.args)
            if tot == 0:
                return json.dumps({'jsonrpc': json_rpc_version, 'error': {'code': -32000, 'message': 'Server error: Generic Zero RPC Exception'}, 'id': serial})
            elif tot == 1:
                return json.dumps({'jsonrpc': json_rpc_version, 'error': {'code': -32001, 'message': 'Server error: ' + exp2.args[0]}, 'id': serial})
            else:
                return json.dumps({'jsonrpc': json_rpc_version, 'error': {'code': exp2.args[1], 'message': 'Server error: ' + exp2.args[0]}, 'id': serial})

        except Exception as exp3:
            return json.dumps({'jsonrpc': json_rpc_version, 'error': {'code': -32603, 'message': 'Internal error: ' + str(exp3)}, 'id': serial})
