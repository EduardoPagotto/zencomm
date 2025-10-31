'''
Created on 20241001
Update on 20251030
@author: Eduardo Pagotto
'''

import zlib
import struct
from enum import Enum
from typing import Tuple

from zen.chunk import Chunk

class ProtocolCode(Enum):
    """[Protocl commands id's]
    Args:
        Enum ([int]): [1 - opem connection
                       2 - Close event
                       3 - Command message
                       4 - Result of Command (3)
                       5 - File Exchange (TODO)
                       255 - Erro Message from host connected]
    """
    OPEN = 1
    CLOSE = 2
    COMMAND = 3
    RESULT = 4
    FILE = 5
    OK = 6 # Return of FILE opp
    ERRO = 255


class Protocol(Chunk):

    def __init__(self, reader, writer):
        super().__init__(reader, writer)

    async def sendProtocol(self, _id : ProtocolCode, _buffer : bytes) -> int:
        """[Send a data buffer to host connected]
        Args:
            _id (ProtocolCode): [id message]
            _buffer (bytes): [buffer data]
        Returns:
            int: [size sended]
        """

        tamanho_buffer : int = int(len(_buffer))
        comprimido :bytes = zlib.compress(_buffer)
        tamanho_comprimido : int = int(len(comprimido))
        crc : int = zlib.crc32(comprimido)

        headerTupleA : Tuple = (_id.value, 0, 0, 0, tamanho_buffer, tamanho_comprimido, crc, 0, 0, 0)
        formatoHeaderA : struct.Struct = struct.Struct('B B B B I I I I I I')
        headerA : bytes = formatoHeaderA.pack(*headerTupleA)

        crc2 :int = zlib.crc32(headerA)
        headerCRC : bytes = struct.pack("I", crc2)

        buffer_final : bytes = headerA + headerCRC + comprimido

        return await self.sendBlocks(buffer_final)

    async def receiveProtocol(self) -> Tuple[ProtocolCode, bytes]:
        """[Receive a data buffer from host connected]
        Raises:
            ExceptionZero: [Fail CRC header]
            ExceptionZero: [Fail CRC checksum]
            ExceptionZero: [Fail to set size buffer]
            ExceptionZeroClose: [Received Close evento from host connected]
            ExceptionZeroErro: [Redeived a erro message from host connected]
        Returns:
            Tuple[ProtocolCode, bytes]: [Code receved, data buffer receved]
        """

        buffer_header = bytearray(await self.receiveBlocks(32))

        formatoHeader = struct.Struct('B B B B I I I I I I I')
        headerTuple = formatoHeader.unpack(buffer_header)

        valInt = int(headerTuple[0])
        idRecebido = ProtocolCode(valInt)

        tamanho_buffer = headerTuple[4]
        tamanho_comprimido = headerTuple[5]
        crc = headerTuple[6]
        crc2 = headerTuple[10]

        bufferHeader = buffer_header[:28]
        crcCalc2 = zlib.crc32(bufferHeader)
        if crc2 != crcCalc2:
            raise Exception('Protocol Receive Header CRC Erro')

        buffer_dados = bytearray(await self.receiveBlocks(tamanho_comprimido))

        crcCalc = zlib.crc32(buffer_dados)

        if crc != crcCalc:
            raise Exception('Protocol Receive Payload CRC Erro')

        binario = zlib.decompress(buffer_dados)

        if len(binario) != tamanho_buffer:
            raise Exception('Protocol Receive size buffer error')

        if idRecebido == ProtocolCode.OPEN:
            msg = binario.decode('UTF-8')

            #self.log.debug('handshake with host:%s', msg)

            await self.sendString(ProtocolCode.RESULT, self.protocol_versao)

        elif idRecebido == ProtocolCode.CLOSE:
            #self.log.debug('closure receved:%s', binario.decode('UTF-8'))
            await self.close()
            #raise Exception('close received:{0}'.format(binario.decode('UTF-8')))

        elif idRecebido == ProtocolCode.ERRO:
            raise Exception('{0}'.format(binario.decode('UTF-8')))

        return idRecebido, binario

    async def sendString(self, _id : ProtocolCode, _texto : str) -> int:
        """[Send a string and code to host connected]
        Args:
            _id (ProtocolCode): [Code of message]
            _texto (str): [Text to send]
        Returns:
            int: [size of message sended]
        """

        buffer = _texto.encode('UTF-8')
        return await self.sendProtocol(_id, buffer)

    async def receiveString(self) -> Tuple[ProtocolCode, str]:
        """[Receive a string and code to host connected]
        Returns:
            Tuple[ProtocolCode, str]: [Code and text receved]
        """

        buffer = await self.receiveProtocol()
        return(buffer[0], buffer[1].decode('UTF-8'))

    async def sendClose(self, _texto : str) -> None:
        """[Send a close command to host if is connected]
        Args:
            _texto (str): [text to host]
        """

        #if self.isConnected() is True:
        #self.log.info('closure sended:%s', _texto)
        await self.sendString(ProtocolCode.CLOSE, _texto)
        await self.close()

    async def handShake(self) -> str:
        """[Execute a exchange of a handshake message to host connected]
        Returns:
            str: [message receved from host connected]
        """
        await self.sendString(ProtocolCode.OPEN, self.protocol_versao)
        idRecive, msg = await self.receiveString()
        if idRecive is ProtocolCode.RESULT:
            #self.log.info('handshake with server: %s', msg)
            return msg

        raise Exception('Fail to Handshake')

    async def exchange(self, input : str) -> str:
        """[Send a text to host and get message back]
        Args:
            input (str): [text to send]
        Raises:
            ExceptionZero: [Fail to get message back]
        Returns:
            str: [text receved]
        """

        await self.sendString(ProtocolCode.COMMAND, input)
        id, msg = await self.receiveString()
        if id == ProtocolCode.RESULT:
            return msg

        raise Exception('Resposta invalida: ({0} : {1})'.format(id, msg))

    async def sendErro(self, msg : str) -> int:
        """[Send a erro Message to the host connected]
        Args:
            msg (str): [message to send]
        Returns:
            int: [size of message sended]
        """
        return self.sendString(ProtocolCode.ERRO, msg)
