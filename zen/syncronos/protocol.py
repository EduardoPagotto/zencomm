'''
Created on 20251107
Update on 20251107
@author: Eduardo Pagotto
'''

from socket import socket
from typing import Tuple

from zen import __version__ as VERSION
from zen.header import ProtocolCode, Header, HEADER_SIZE, BLOCK_SIZE

class Protocol(object):
    def __init__(self, sock : socket):
        self.sock = sock
        self.version = VERSION
        self.peer_version = ''

    def __sendBlocks(self, _buffer : bytes) -> int:

        total_enviado : int = 0
        total_buffer :int = len(_buffer)
        while total_enviado < total_buffer:
            tam : int = total_buffer - total_enviado
            if tam > BLOCK_SIZE:
                tam = BLOCK_SIZE

            inicio = total_enviado
            fim = total_enviado + tam

            sub_buffer = bytearray(_buffer[inicio:fim])
            sent = self.sock.send(sub_buffer)
            if sent == 0:
                raise Exception("send block fail")

            total_enviado = fim

        return total_enviado

    def __receiveBlocks(self, _tamanho : int) -> bytes:

        total_recebido : int = 0
        buffer_local : bytes = bytes()

        while total_recebido < _tamanho:
            tam : int = _tamanho - total_recebido
            if tam > BLOCK_SIZE:
                tam = BLOCK_SIZE

            # chunk : bytes = await self.__reader.readexactly(tam)
            chunk : bytes = self.sock.recv(tam)

            if chunk == b'':
                raise Exception("receive empty block")

            buffer_local += chunk

            total_recebido = len(buffer_local)

        return buffer_local

    def _sendProtocol(self, _id : ProtocolCode, _buffer : bytes) -> int:

        header = Header(id=_id)
        return self.__sendBlocks(header.encode(_buffer))

    def _receiveProtocol(self) -> Tuple[ProtocolCode, bytes]:

        header = Header()

        header.decode_h(self.__receiveBlocks(HEADER_SIZE))

        binario = header.decode_d(self.__receiveBlocks(header.size_zip))

        if header.id == ProtocolCode.OPEN:
            self.peer_version = binario.decode('UTF-8')
            #self.log.debug('handshake with host:%s', msg)
            self.sendString(ProtocolCode.RESULT, self.version)

        elif header.id == ProtocolCode.CLOSE:
            #self.log.debug('closure receved:%s', binario.decode('UTF-8'))
            self.close()
            #raise Exception('close received:{0}'.format(binario.decode('UTF-8')))

        elif header.id == ProtocolCode.ERRO:
            raise Exception('{0}'.format(binario.decode('UTF-8')))

        return ProtocolCode(header.id), binario

    def close(self):
        self.sock.close()

    def sendString(self, _id : ProtocolCode, _texto : str) -> int:

        return self._sendProtocol(_id, _texto.encode('UTF-8'))

    def receiveString(self) -> Tuple[ProtocolCode, str]:

        buffer = self._receiveProtocol()
        return(buffer[0], buffer[1].decode('UTF-8'))

    def sendClose(self, _texto : str) -> None:

        self.sendString(ProtocolCode.CLOSE, _texto)
        self.close()

    def handShake(self) -> str:

        self.sendString(ProtocolCode.OPEN, self.version)
        idRecive, msg = self.receiveString()
        if idRecive is ProtocolCode.RESULT:
            #self.log.info('handshake with server: %s', msg)
            return msg

        raise Exception('Fail to Handshake')

    def exchange(self, input : str) -> str:

        self.sendString(ProtocolCode.COMMAND, input)
        id, msg = self.receiveString()
        if id == ProtocolCode.RESULT:
            return msg

        raise Exception('Resposta invalida: ({0} : {1})'.format(id, msg))

    def sendErro(self, msg : str) -> int:
        return self.sendString(ProtocolCode.ERRO, msg)
