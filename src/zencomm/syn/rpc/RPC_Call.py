'''
Created on 20190823
Update on 20220926
@author: Eduardo Pagotto
'''

import threading
import random

from zencomm import __json_rpc_version__ as json_rpc_version
from zencomm import ExceptZen

from .ConnectionControl import ConnectionControl

class RPC_Call(object):
    """[Midlleware json Protocol]
    Args:
        object ([type]): [description]
    Raises:
        ExceptionRPC: [Raised exception on Server of RPC]
        ExceptionRPC: [FATAL!!! invalid ID]
    Returns:
        [type]: [description]
    """

    __serial_lock : threading.Lock = threading.Lock()
    __serial : int = random.randint(0,10000)

    def __init__(self, nome_metodo : str, control : ConnectionControl):
        """[Constructor json message builder]
        Args:
            nome_metodo (str): [method name do send to Server of RPC]
            control (ConnectionControl): [Valid Connection with Server RPC]
        """

        self.serial : int = RPC_Call.__createId()
        self.method : str = nome_metodo
        self.control : ConnectionControl = control

    @staticmethod
    def __createId() -> int:
        """[Identicatos Json Protocol]
        Returns:
            int: [description]
        """
        with RPC_Call.__serial_lock:
            serial = RPC_Call.__serial
            RPC_Call.__serial += 1

            return serial

    def encode(self, *args, **kargs) -> dict:
        """[encode json Protocol]
        Returns:
            str: [json with data encoded]
        """

        keys = {}
        arguments = []
        if args:
            arguments = args[0]
            keys = args[1]

        return {'jsonrpc':json_rpc_version, 'id':self.serial, 'method': self.method, 'params': arguments, 'keys': keys}


    def decode(self, reg : dict) -> dict:
        """[decode json Protocol]
        Args:
            reg (dict): [rpc fields]
        Raises:
            ExceptionRPC: [Raised exception on Server of RPC]
            ExceptionRPC: [FATAL!!! invalid ID]
        Returns:
            dict: [Result os fields]
        """
        if reg['id'] == self.serial:
            if 'error' in reg:
                raise ExceptZen(reg['error']['message'], reg['error']['code'])

            return reg['result']

        raise ExceptZen(f'Parse error, id {reg["id"]} should be {self.serial}', -32700)

    def __call__(self, *args, **kargs) -> dict:
        """[Call RPC on connection and get result]
        Returns:
            (dict): [Result of RPC call]
        """
        return self.decode(self.control.exec(self.encode(args, kargs), args, kargs))
