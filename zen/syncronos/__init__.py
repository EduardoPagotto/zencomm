'''
Created on 20241001
Update on 20251108
@author: Eduardo Pagotto
'''

import logging
import sys

from pathlib import Path

_gslogger = None

def get_logger(name: str = '') -> logging.Logger:

    global _gslogger

    if _gslogger is not None:
        return _gslogger

    Path('./log').mkdir(parents=True, exist_ok=True)

    log_format = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s\t\t %(message)s",
        datefmt="%Y%m%d %H:%M:%S"
    )

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.formatter = log_format

    #stderr_handler = AsyncStreamHandler(stream=sys.stderr)
    #stderr_handler.formatter = log_format

    #file_handler = AsyncFileHandler(filename='./log/server.log')
    #file_handler.formatter = log_format

    logger = logging.Logger(name=name, level=logging.DEBUG)
    #logger.add_handler(file_handler)
    logger.addHandler(stdout_handler)
    #logger.add_handler(stderr_handler)
    #logger.info("Start logger")

    _gslogger = logger

    return _gslogger
