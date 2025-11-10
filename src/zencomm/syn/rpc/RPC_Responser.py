'''
Created on 20190824
Update on 20251110
@author: Eduardo Pagotto
'''

from zencomm import ExceptZen, __json_rpc_version__ as json_rpc_version

class RPC_Responser(object):
    """[Connection thread with server RPC ]
    Args:
        object ([type]): [description]
    """

    def __init__(self, target : object):
        """[summary]
        Args:
            target (object): [Method Name to run in RPC Server]
        """
        self.target : object = target

    def encode_exec_decode(self, reg: dict) -> dict:
        serial : int = reg['id']
        metodo : str = reg['method']

        try:
            val = getattr(self.target, metodo)(*reg['params'], **reg['keys'])
            return {'jsonrpc': json_rpc_version, 'result': val, 'id': serial}

        except AttributeError as exp:
            return {'jsonrpc': json_rpc_version, 'error': {'code': -32601, 'message': 'Method not found: '+ str(exp)}, 'id': serial}

        except TypeError as exp1:
            return {'jsonrpc': json_rpc_version, 'error': {'code': -32602, 'message': 'Invalid params: '+ str(exp1)}, 'id': serial}

        except ExceptZen as exp2:
            tot = len(exp2.args)
            if tot == 0:
                return {'jsonrpc': json_rpc_version, 'error': {'code': -32000, 'message': 'server error: generic RPC exception'}, 'id': serial}
            elif tot == 1:
                return {'jsonrpc': json_rpc_version, 'error': {'code': -32001, 'message': 'server error: ' + exp2.args[0]}, 'id': serial}
            else:
                return {'jsonrpc': json_rpc_version, 'error': {'code': exp2.args[1], 'message': 'server error: ' + exp2.args[0]}, 'id': serial}

        except Exception as exp3:
            return {'jsonrpc': json_rpc_version, 'error': {'code': -32603, 'message': 'server side error: ' + str(exp3.args[0])}, 'id': serial}
