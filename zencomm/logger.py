'''
Created on 20251112
Update on 20251112
@author: Eduardo Pagotto
'''

import logging
import logging.handlers
from logging.handlers import RotatingFileHandler

from pathlib import Path
import queue
import sys
import atexit

def setup_queue_logging(filelog : str) -> logging.handlers.QueueListener:
    log_queue = queue.Queue()
    queue_handler = logging.handlers.QueueHandler(log_queue)

    # Configurar o logger principal para usar o QueueHandler não bloqueante
    root_logger = logging.getLogger()
    root_logger.addHandler(queue_handler)
    root_logger.setLevel(logging.INFO)

    # Formatador geral
    log_format = logging.Formatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(threadName)s %(funcName)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    #fmt="%(asctime)s - %(levelname)s - %(name)s %(message)s",
    #fmt='%(asctime)s %(name)-12s %(levelname)-8s %(threadName)-16s %(funcName)-20s %(message)s',

    # Handler de stream
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(log_format)

    # Handler de file
    Path('./log').mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(filelog, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(log_format)

    # Criar e iniciar o listener em um thread separado
    queue_listener = logging.handlers.QueueListener(log_queue, file_handler,
                                                               stdout_handler)
    queue_listener.start()

    # Register atexit to stop the listener gracefully on program exit
    atexit.register(queue_listener.stop)
    return queue_listener

# def log_teste():
#     log = logging.getLogger(__name__)
#     log.info('AAAAA')
#     log.warning('bbbb')

# def main():

#     log_listener = setup_queue_logging('./log/central.log')
#     #log_listener.
#     log = logging.getLogger("central")

#     log.info("teste 123....")
#     log.warning("teste 123....")
#     log.error("teste 123....")
