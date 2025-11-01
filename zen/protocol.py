'''
Created on 20241001
Update on 20251031
@author: Eduardo Pagotto
'''

from typing import Tuple

from zen.header import ProtocolCode, Header, HEADER_SIZE
from zen.chunk import Chunk

class Protocol(Chunk):

    def __init__(self, reader, writer):
        super().__init__(reader, writer)

    async def _sendProtocol(self, _id : ProtocolCode, _buffer : bytes) -> int:

        header = Header(id=_id)

        return await self.sendBlocks(header.pack(_buffer))

    async def _receiveProtocol(self) -> Tuple[ProtocolCode, bytes]:

        header = Header()

        header.receive(await self.receiveBlocks(HEADER_SIZE))

        binario = header.unpack(await self.receiveBlocks(header.size_zip))

        if header.id == ProtocolCode.OPEN:
            msg = binario.decode('UTF-8')
            #self.log.debug('handshake with host:%s', msg)
            await self.sendString(ProtocolCode.RESULT, self.protocol_versao)

        elif header.id == ProtocolCode.CLOSE:
            #self.log.debug('closure receved:%s', binario.decode('UTF-8'))
            await self.close()
            #raise Exception('close received:{0}'.format(binario.decode('UTF-8')))

        elif header.id == ProtocolCode.ERRO:
            raise Exception('{0}'.format(binario.decode('UTF-8')))

        return header.id, binario

    async def sendString(self, _id : ProtocolCode, _texto : str) -> int:

        return await self._sendProtocol(_id, _texto.encode('UTF-8'))

    async def receiveString(self) -> Tuple[ProtocolCode, str]:

        buffer = await self._receiveProtocol()
        return(buffer[0], buffer[1].decode('UTF-8'))

    async def sendClose(self, _texto : str) -> None:

        await self.sendString(ProtocolCode.CLOSE, _texto)
        await self.close()

    async def handShake(self) -> str:

        await self.sendString(ProtocolCode.OPEN, self.protocol_versao)
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
