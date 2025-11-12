'''
Created on 20241001
Update on 20251111
@author: Eduardo Pagotto
'''

__version__ : str = "1.2.3"

from zencomm.header import ProtocolCode
from zencomm.utils import GracefulKiller

class ExceptZen(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
