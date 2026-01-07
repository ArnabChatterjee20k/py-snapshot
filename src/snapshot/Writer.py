from typing import BinaryIO
import struct
from .TypeHandler import EncodingTypes, VariableLengthEncodingMarkers, ALL_SET_MARKER
import zlib


class Writer:
    def __init__(self, source: dict = None, buffer: BinaryIO = None):
        self._buffer: BinaryIO = buffer
        self._source: dict = source

    def set_buffer(self, buffer: BinaryIO):
        self._buffer = buffer

    def set_source(self, source: dict):
        self._source = source

    @property
    def buffer(self):
        return self._buffer

    def write_encoding(self, encoding: EncodingTypes):
        # write with a prefix of 11
        self._buffer.write(bytes([3 << 6 | encoding.value]))

    def write_value(self, value) -> int:
        "Write the value to the buffer in compressed string format"
        value = str(value)

        # try compression and if length coming small then only use the compressed value
        original_length = len(value.encode("utf-8"))
        compressed = zlib.compress(value.encode())
        compressed_length = len(compressed)

        if compressed_length < original_length:
            self.write_encoding(EncodingTypes.COMPRESSED)
            return sum(self.write_length(compressed_length), compressed)

        # no compression marker
        return sum(self.write_length(original_length), value)

    def write_length(self, length: int) -> int:
        "Returns number of bytes written"
        if length <= VariableLengthEncodingMarkers.SIX_BIT_ENCODING.value:
            self._buffer.write(bytes([length]))
            return 1

        if length <= VariableLengthEncodingMarkers.FORTEEN_BIT_ENCODING:
            # we need to pack the whole byte into two bytes
            # basically inside 14 bits as first bit will be for marker
            # overflow and padding it with marker
            # doing | 64 will add the prefix 64
            first_byte = (length >> 8) | 64
            second_byte = length & ALL_SET_MARKER

            self._buffer.write(bytes([first_byte, second_byte]))
            return 2

        self._buffer.write(
            bytes(
                [
                    VariableLengthEncodingMarkers.THIRTY_TWO_BIT_ENCODING,
                    struct.pack("<I", length),
                ]
            )
        )
        return 5
