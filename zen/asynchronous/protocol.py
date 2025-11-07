'''
Created on 20241001
Update on 20251107
@author: Eduardo Pagotto
'''

from typing import Tuple
from zen.header import ProtocolCode, Header, HEADER_SIZE, BLOCK_SIZE

class Protocol(object):

    def __init__(self, reader, writer):
        self.__reader = reader
        self.__writer = writer
        self.version = '0.0.1'
        self.peer_version = ''

    async def __sendBlocks(self, _buffer : bytes) -> int:

        total_enviado : int = 0
        total_buffer :int = len(_buffer)
        while total_enviado < total_buffer:
            tam : int = total_buffer - total_enviado
            if tam > BLOCK_SIZE:
                tam = BLOCK_SIZE

            inicio = total_enviado
            fim = total_enviado + tam

            sub_buffer = bytearray(_buffer[inicio:fim])
            self.__writer.write(sub_buffer)
            await self.__writer.drain()

            total_enviado = fim

        return total_enviado

    async def __receiveBlocks(self, _tamanho : int) -> bytes:

        total_recebido : int = 0
        buffer_local : bytes = bytes()

        while total_recebido < _tamanho:
            tam : int = _tamanho - total_recebido
            if tam > BLOCK_SIZE:
                tam = BLOCK_SIZE

            chunk : bytes = await self.__reader.readexactly(tam)

            if chunk == b'':
                raise Exception("receive empty block")

            buffer_local += chunk

            total_recebido = len(buffer_local)

        return buffer_local

    async def _sendProtocol(self, _id : ProtocolCode, _buffer : bytes) -> int:

        header = Header(id=_id)

        return await self.__sendBlocks(header.encode(_buffer))

    async def _receiveProtocol(self) -> Tuple[ProtocolCode, bytes]:

        header = Header()

        header.decode_h(await self.__receiveBlocks(HEADER_SIZE))

        binario = header.decode_d(await self.__receiveBlocks(header.size_zip))

        if header.id == ProtocolCode.OPEN:
            self.peer_version = binario.decode('UTF-8')
            #self.log.debug('handshake with host:%s', msg)
            await self.sendString(ProtocolCode.RESULT, self.version)

        elif header.id == ProtocolCode.CLOSE:
            #self.log.debug('closure receved:%s', binario.decode('UTF-8'))
            await self.close()
            #raise Exception('close received:{0}'.format(binario.decode('UTF-8')))

        elif header.id == ProtocolCode.ERRO:
            raise Exception('{0}'.format(binario.decode('UTF-8')))

        return ProtocolCode(header.id), binario

    async def close(self):
        self.__writer.close()
        await self.__writer.wait_closed()

    async def sendString(self, _id : ProtocolCode, _texto : str) -> int:

        return await self._sendProtocol(_id, _texto.encode('UTF-8'))

    async def receiveString(self) -> Tuple[ProtocolCode, str]:

        buffer = await self._receiveProtocol()
        return(buffer[0], buffer[1].decode('UTF-8'))

    async def sendClose(self, _texto : str) -> None:

        await self.sendString(ProtocolCode.CLOSE, _texto)
        await self.close()

    async def handShake(self) -> str:

        await self.sendString(ProtocolCode.OPEN, self.version)
        idRecive, msg = await self.receiveString()
        if idRecive is ProtocolCode.RESULT:
            #self.log.info('handshake with server: %s', msg)
            return msg

        raise Exception('Fail to Handshake')

    async def exchange(self, input : str) -> str:

        await self.sendString(ProtocolCode.COMMAND, input)
        id, msg = await self.receiveString()
        if id == ProtocolCode.RESULT:
            return msg

        raise Exception('Resposta invalida: ({0} : {1})'.format(id, msg))

    async def sendErro(self, msg : str) -> int:
        return await self.sendString(ProtocolCode.ERRO, msg)
