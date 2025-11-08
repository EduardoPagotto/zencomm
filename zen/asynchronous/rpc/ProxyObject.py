'''
Created on 20190822
Update on 20210212
@author: Eduardo Pagotto
'''

from typing import Any

from .RPC_Call import RPC_Call
from .ConnectionControl import ConnectionControl

class ProxyObject(object):
    """[Client Proxy Wrapper]
    Args:
        object ([type]): [description]
    """
    def __init__(self, conn_control : ConnectionControl):
        self.conn_control = conn_control

    def __getattr__(self, name : str) -> RPC_Call:
        """[summary]
        Args:
            name (str): [name of method]
        Returns:
            RPC_Call: [object wrapper]
        """
        return RPC_Call(name, self.conn_control)

    def __setattr__(self, name : str, value : Any) -> None:
        """[New Sttribute]
        Args:
            name (str): [Name]
            value (Any): [object]
        """
        self.__dict__[name] = value
