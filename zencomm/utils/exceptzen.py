'''
Created on 20251112
Update on 20251112
@author: Eduardo Pagotto
'''

class ExceptZen(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
