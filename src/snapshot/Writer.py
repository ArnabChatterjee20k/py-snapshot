from typing import BinaryIO
import struct
import zlib
from .TypeHandler import (
    TypeHandler,
    EncodingTypes,
    VariableLengthEncodingMarkers,
    ALL_SET_MARKER,
)
from .TypeRegistry import TypeNotFoundException


class Writer:
    def __init__(self, source: dict = None, buffer: BinaryIO = None):
        # to avoid partial imports
        from . import registry

        self._registry = registry
        self._buffer: BinaryIO = buffer
        self._source: dict = source

    def set_buffer(self, buffer: BinaryIO):
        self._buffer = buffer

    def set_source(self, source: dict):
        self._source = source

    @property
    def buffer(self):
        return self._buffer

    def write(self):
        self.write_length(len(self._source))
        for key, value in self._source.items():
            self.write_key_value(key, value)
        self.write_encoding(EncodingTypes.EOF)

    def write_encoding(self, encoding: EncodingTypes):
        # write with a prefix of 11
        self._buffer.write(bytes([3 << 6 | encoding.value]))

    def write_key_value(self, key, value) -> int:
        handler, written = self.write_object_id(value)
        # key length + data
        written += self.write_value(key)
        written += handler.serialise(self, value)
        return written

    # HACK: a very anti pattern to return hander + int from a writer
    def write_object_id(self, value) -> tuple[TypeHandler, int]:
        handler = self._registry.get_handler_by_type(type(value))
        if not handler:
            raise TypeNotFoundException(f"Type handler not found for {type(value)}")
        object_type = handler.type_identifier
        return handler, self.buffer.write(bytes([object_type]))

    def write_value(self, value) -> int:
        "Write the value to the buffer in compressed string format"
        value = (str(value)).encode("utf-8")

        # try compression and if length coming small then only use the compressed value
        original_length = len(value)
        compressed = zlib.compress(value)
        compressed_length = len(compressed)

        if compressed_length < original_length:
            self.write_encoding(EncodingTypes.COMPRESSED)
            return self.write_length(compressed_length) + self._buffer.write(compressed)

        # no compression marker
        return self.write_length(original_length) + self._buffer.write(value)

    def write_length(self, length: int) -> int:
        "Returns number of bytes written"
        if length <= VariableLengthEncodingMarkers.SIX_BIT_ENCODING.value:
            self._buffer.write(bytes([length]))
            return 1

        if length <= VariableLengthEncodingMarkers.FORTEEN_BIT_ENCODING.value:
            # we need to pack the whole byte into two bytes
            # basically inside 14 bits as first bit will be for marker
            # overflow and padding it with marker
            # doing | 64 will add the prefix 64
            first_byte = (length >> 8) | 64
            second_byte = length & ALL_SET_MARKER

            self._buffer.write(bytes([first_byte, second_byte]))
            return 2

        # writing explicitly as struct returns bytes so bytes
        self._buffer.write(
            bytes([VariableLengthEncodingMarkers.THIRTY_TWO_BIT_ENCODING])
        )
        self._buffer.write(struct.pack("<I", length))
        return 5
