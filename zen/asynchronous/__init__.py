'''
Created on 20241001
Update on 20251107
@author: Eduardo Pagotto
'''

import sys
from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.levels import LogLevel

from pathlib import Path

_glogger = None

# from zen.asynchronous.protocol import Protocol
# from zen.asynchronous.socket import socket_client, SocketServer

def get_async_logger(name: str = '') -> Logger:

    global _glogger

    if _glogger is not None:
        return _glogger

    Path('./log').mkdir(parents=True, exist_ok=True)

    log_format = Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s\t\t %(message)s",
        datefmt="%Y%m%d %H:%M:%S"
    )

    stdout_handler = AsyncStreamHandler(stream=sys.stdout)
    stdout_handler.formatter = log_format

    #stderr_handler = AsyncStreamHandler(stream=sys.stderr)
    #stderr_handler.formatter = log_format

    #file_handler = AsyncFileHandler(filename='./log/server.log')
    #file_handler.formatter = log_format

    logger = Logger(name=name, level=LogLevel.DEBUG) #Logger.with_default_handlers(name=name, level=LogLevel.DEBUG)
    #logger.add_handler(file_handler)
    logger.add_handler(stdout_handler)
    #logger.add_handler(stderr_handler)
    #logger.info("Start logger")

    _glogger = logger

    return _glogger
