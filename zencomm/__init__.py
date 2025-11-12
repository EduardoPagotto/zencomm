'''
Created on 20241001
Update on 20251111
@author: Eduardo Pagotto
'''

__version__ : str = "2.0.0"

from zencomm.header import ProtocolCode
from zencomm.utils import GracefulKiller,Singleton, ExceptZen
from zencomm.logger import setup_queue_logging
