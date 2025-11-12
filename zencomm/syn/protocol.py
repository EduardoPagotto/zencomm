'''
Created on 20251107
Update on 20251111
@author: Eduardo Pagotto
'''

import os
from socket import socket
from typing import Tuple

from zencomm import ExceptZen, __version__ as VERSION
from zencomm.header import ProtocolCode, Header, HEADER_SIZE, BLOCK_SIZE

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

    def sendBin(self, buffer : bytes):
        """[Send a Binary data to host connected]
        Args:
            buffer (bytes): [buffer of data]
        Raises:
            ExceptionZero: [Fail to read a file from disk]
            ExceptionZero: [Fail to acess a file from disk]
            ExceptionZero: [host connected return a erro mensage]
        Returns:
            int: [size of file sended]
        """
        self._sendProtocol(ProtocolCode.FILE, buffer)
        idRecebido, msg = self.receiveString()
        if idRecebido is not ProtocolCode.OK or msg != 'OK':
            raise ExceptZen(f'ACK send file erro {msg}')

    def sendFile(self, path_file_name : str) -> int:
        """[Send a file to host connected]
        Args:
            path_file_name (str): [path of file]
        Raises:
            ExceptionZero: [Fail to read a file from disk]
            ExceptionZero: [Fail to acess a file from disk]
            ExceptionZero: [host connected return a erro mensage]
        Returns:
            int: [size of file sended]
        """
        fileContent = None
        tamanho_arquivo = 0
        try:
            with open(path_file_name, mode='rb') as file:
                fileContent = file.read()
                tamanho_arquivo = len(fileContent)

        except IOError as e:
            msg_erro = f'Error IO file{path_file_name} :{str(e)}'
            self.sendErro(msg_erro)
            raise ExceptZen(msg_erro)

        except Exception as exp:
            msg_erro = f'Critical error IO file{path_file_name} :{str(exp)}'
            self.sendErro(msg_erro)
            raise ExceptZen(msg_erro)

        self._sendProtocol(ProtocolCode.FILE, fileContent)
        idRecebido, msg = self.receiveString()

        if idRecebido is not ProtocolCode.OK or msg != 'OK':
            raise ExceptZen('Protocolo Send Falha no ACK do arquivo:{0} Erro:{1}'.format(path_file_name, msg))

        return tamanho_arquivo

    def receiveBin(self) -> bytes:
        id, buffer = self._receiveProtocol()
        if id == ProtocolCode.FILE:
            self.sendString(ProtocolCode.OK, 'OK')
        elif id == ProtocolCode.ERRO:
            msg_erro = f'Error Recive bin: {buffer.decode("UTF-8")}'
            self.sendErro(msg_erro)
            raise ExceptZen(msg_erro)

        return buffer

    def receiveFile(self, path_file_name : str) -> int:
        """[Receive a file from host connected]
        Args:
            path_file_name (str): [path to save a file]
        Raises:
            ExceptionZero: [Fail to create a dir]
            Exception: [Fail to save a file]
            Exception: [Receive a unspected command]
        Returns:
            int: [description]
        """
        id, buffer_arquivo = self._receiveProtocol()

        path, file_name = os.path.split(path_file_name)
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError as e:
            msg_erro = f'Error mkdir:{path_file_name} Erro:{str(e)}'
            self.sendErro(msg_erro)
            raise ExceptZen(msg_erro)

        if id == ProtocolCode.FILE:
            try:
                with open(path_file_name, mode='wb') as file:
                    #file.write(bytes(int(x, 0) for x in buffer_arquivo))
                    file.write(buffer_arquivo)
                    self.sendString(ProtocolCode.OK, 'OK')
                    return len(buffer_arquivo)

            except Exception as exp:
                msg_erro = 'Erro ao gravar arquivo:{0} Erro:{1}'.format(path_file_name, str(exp))
                self.sendErro(msg_erro)
                raise Exception(msg_erro)

        else:
            msg_erro = 'Nao recebi o arquivo:{0} Erro ID:{1}'.format(path_file_name, str(id))
            self.sendErro(msg_erro)
            raise Exception(msg_erro)
