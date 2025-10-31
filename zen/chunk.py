'''
Created on 20241001
Update on 20251030
@author: Eduardo Pagotto
'''

BLOCK_SIZE = 2048

class Chunk(object):

    def __init__(self, reader, writer):
        self.__reader = reader
        self.__writer = writer

    async def sendBlocks(self, _buffer : bytes) -> int:
        """[Send chunk's to host connected]
        Args:
            _buffer (bytes): [Data to transfer]
        Returns:
            int: [Total receved]
        """

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

    async def receiveBlocks(self, _tamanho : int) -> bytes:
        """[Receive chunk's from host connected]
        Args:
            _tamanho (int): [total to receve]
        Raises:
            ExceptionZero: [Raise if chunk's fail]
        Returns:
            bytes: [Buffer with data receved]
        """

        total_recebido : int = 0
        buffer_local : bytes = bytes()

        while total_recebido < _tamanho:
            tam : int = _tamanho - total_recebido
            if tam > BLOCK_SIZE:
                tam = BLOCK_SIZE

            chunk : bytes = await self.__reader.readexactly(tam)

            if chunk == b'':
                raise Exception("Fail Receive a chunk")

            buffer_local += chunk

            total_recebido = len(buffer_local)

        return buffer_local

    async def close(self):
        self.__writer.close()
        await self.__writer.wait_closed()
