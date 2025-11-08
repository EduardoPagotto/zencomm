'''
Created on 20190824
Update on 20251108
@author: Eduardo Pagotto
'''

import socket
import json

from zen import ExceptZen, __json_rpc_version__ as json_rpc_version

from zen.asynchronous import get_async_logger
from zen.asynchronous.protocol import Protocol
from zen.header import ProtocolCode

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
        self.log = get_async_logger()
        self.target : object= target

    async def __call__(self, *args, **kargs):
        """[execute exchange of json's messages with server RPC]
        """
        #done = args[2]

        await self.log.info('start responcer')

        protocol = None
        try:
            protocol = Protocol(args[0], args[1])
            #protocol.settimeout(30)

        except Exception as exp:
            self.log.critical('fail creating connection: %s', str(exp))
            return

        count_to = 0

        while True:
            try:
                count_to = 0
                idRec, buffer = await protocol._receiveProtocol()
                if idRec == ProtocolCode.COMMAND:
                    await protocol.sendString(ProtocolCode.RESULT, await self.rpc_exec_func(buffer.decode('UTF-8'), protocol))

                elif idRec == ProtocolCode.CLOSE:
                    await self.log.debug(f'responser receive {buffer.decode('UTF-8')}')
                    break

            # except ExceptionZeroErro as exp_erro:
            #     self.log.error('%s recevice erro: %s',t_name, str(exp_erro))
            #     await protocol.sendString(ProtocolCode.RESULT, 'recived error from server')

            # except ExceptionZeroClose as exp_close:
            #     self.log.warning('%s %s',t_name, str(exp_close))
            #     break

            except socket.timeout:
                count_to += 1
                self.log.warning('responser TO count: %d', count_to)

            except Exception as exp:
                self.log.error('responser exception error: %s', str(exp))
                break

        await protocol.close()

        self.log.info('responser finnished')

    async def rpc_exec_func(self, msg : str, protocol : Protocol) -> str:
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
            val = await getattr(self.target, metodo)(*dados['params'], **dados['keys'])
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
