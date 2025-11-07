'''
Created on 20251031
Update on 20251107
@author: Eduardo Pagotto
'''

import struct
import zlib
from typing import Tuple
from dataclasses import dataclass
from enum import IntEnum

class ProtocolCode(IntEnum):
    OPEN = 1
    CLOSE = 2
    COMMAND = 3
    RESULT = 4
    FILE = 5
    OK = 6 # Return of FILE opp
    ERRO = 255

HEADER_SIZE = 32
BLOCK_SIZE = 2048

@dataclass
class Header:
    id: int = 0        # [0]   # 0,1,2,3
    size: int = 0      # [1]   # 4,5,6,7
    size_zip: int = 0  # [2]   # 8,9,10,11
    crc_zip: int = 0   # [3]   # 12,13,14,15
    resi0: int = 0     # [4]   # 16,17,18,19
    resi1: int = 0     # [5]   # 20.21.22.23
    resi2: int = 0     # [6]   # 24,25,26,27
    crc_header: int = 0# [7]   # 28,29,30,31

    def encode(self, buffer : bytes) -> bytes:

        # zip data
        zipped : bytes = zlib.compress(buffer)

        self.size = len(buffer)
        self.size_zip = len(zipped)
        self.crc_zip = zlib.crc32(zipped)

        # binary header without header-crc !!!
        headerTupleA : Tuple = (self.id, self.size, self.size_zip, self.crc_zip, 0, 0, 0)
        formatoHeaderA : struct.Struct = struct.Struct('I I I I I I I')
        headerA : bytes = formatoHeaderA.pack(*headerTupleA)

        # calc crc header only
        self.crc_header = zlib.crc32(headerA)
        headerCRC : bytes = struct.pack("I", self.crc_header)

        # append all
        buffer_complet : bytes = headerA + headerCRC + zipped

        return buffer_complet

    def decode_h(self, data_in : bytes):

        buffer_header = bytearray(data_in)

        formatoHeader = struct.Struct('I I I I I I I I')
        headerTuple = formatoHeader.unpack(buffer_header)

        self.id = ProtocolCode(int(headerTuple[0]))
        self.size = int(headerTuple[1])
        self.size_zip = int(headerTuple[2])
        self.crc_zip = int(headerTuple[3])
        self.crc_header = int(headerTuple[7])

        inner_fields = buffer_header[:28] # ou 27??
        crc_header_recive = zlib.crc32(inner_fields)

        if self.crc_header != crc_header_recive:
            raise Exception('wrong header crc')

    def decode_d(self, buffer : bytes) -> bytes:
        buffer_dados = bytearray(buffer)

        crcCalc = zlib.crc32(buffer_dados)
        if self.crc_zip != crcCalc:
            raise Exception('wrong payload crc')

        binario = zlib.decompress(buffer_dados)

        if len(binario) != self.size:
            raise Exception('wrong payload size')

        return binario
