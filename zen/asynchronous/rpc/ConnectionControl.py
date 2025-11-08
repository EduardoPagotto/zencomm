'''
Created on 20190914
Update on 20220926
@author: Eduardo Pagotto
'''

from abc import ABC, abstractmethod

class ConnectionControl(ABC):
    def __init__(self, addr : str):
        self.__addr = addr

    def getUrl(self) -> str:
        return self.__addr

    @abstractmethod
    async def exec(self, input_rpc : dict, *args, **kargs) -> dict:
        return {}
