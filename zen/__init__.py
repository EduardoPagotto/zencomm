'''
Created on 20241001
Update on 20251108
@author: Eduardo Pagotto
'''

__json_rpc_version__ : str = '2.0'
__version__ : str = "1.2.3"

class ExceptZen(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
