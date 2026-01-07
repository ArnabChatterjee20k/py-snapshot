from typing import BinaryIO
import struct
from .TypeHandler import EncodingTypes, VariableLengthEncodingMarkers, ALL_SET_MARKER
import zlib


class Reader:
    def __init__(self, destination: dict = None, buffer: BinaryIO = None):
        self._buffer: BinaryIO = buffer
        self._destination: dict = destination

    def set_buffer(self, buffer: BinaryIO):
        self._buffer = buffer

    def set_destination(self, destination: dict):
        self._destination = destination

    @property
    def buffer(self):
        return self._buffer

    def read_encoding(self):
        first_byte = self._buffer.read(1)[0]
        # prefix 11
        if first_byte >> 6 == 3:
            return EncodingTypes(first_byte & 0x3F)
        self.buffer.seek(-1, 1)
        return None

    def read_value(self, encoding: EncodingTypes = None):
        length = self.read_length()
        if encoding == EncodingTypes.COMPRESSED:
            data = self._buffer.read(length)
            return zlib.decompress(data).decode()
        return self._buffer.read(length).decode("utf-8")

    def read_length(self):
        length = self._buffer.read(1)[0]
        marker_with_first_byte = length[0]

        if (
            marker_with_first_byte
            <= VariableLengthEncodingMarkers.SIX_BIT_ENCODING.value
        ):
            # since marker itself the length due to the 00 prefix
            return marker_with_first_byte

        # 0x3F mask out the marker as it is 6bits and give the 6bits only out of 8bits
        first_byte = marker_with_first_byte & 0x3F
        if (
            marker_with_first_byte
            <= VariableLengthEncodingMarkers.FORTEEN_BIT_ENCODING.value
        ):
            second_byte = self.buffer.read(1)[0]
            return (first_byte << 8) | second_byte

        return struct.unpack("<I", self.buffer.read(4)[0])
