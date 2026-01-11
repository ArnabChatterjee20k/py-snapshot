from typing import BinaryIO
import struct
from .TypeHandler import (
    TypeHandler,
    EncodingTypes,
    VariableLengthEncodingMarkers,
    ALL_SET_MARKER,
)
from .TypeRegistry import TypeNotFoundException
import zlib


class Reader:
    def __init__(self, buffer: BinaryIO = None):
        from . import registry

        self._registry = registry
        self._buffer: BinaryIO = buffer

    def set_buffer(self, buffer: BinaryIO):
        self._buffer = buffer

    @property
    def buffer(self):
        return self._buffer

    def read(self) -> dict:
        if not self._buffer:
            return {}
        length = self.read_length()
        result = {}

        for _ in range(length):
            key, value = self.read_key_value()
            if key is None or value is None:
                break
            result[key] = value

        encoding = self.read_encoding()
        if encoding == EncodingTypes.EOF:
            pass

        return result

    def read_encoding(self):
        first_byte = self._buffer.read(1)[0]
        # prefix 11
        if first_byte >> 6 == 3:
            return EncodingTypes(first_byte & 0x3F)
        self.buffer.seek(-1, 1)
        return None

    def read_object_id(self) -> tuple[TypeHandler, int]:
        current_pos = self._buffer.tell()
        encoding = self.read_encoding()

        if encoding == EncodingTypes.EOF:
            return None, 1

        self._buffer.seek(current_pos)
        current = self._buffer.read(1)
        if not current:
            return None, None

        object_type_id = current[0]

        handler = self._registry.get_handler_by_id(object_type_id)
        if not handler:
            raise TypeNotFoundException(
                f"Handler not found for type ID {object_type_id}"
            )

        return handler, 1

    def read_value(self, encoding: EncodingTypes = None):
        length = self.read_length()
        if encoding == EncodingTypes.COMPRESSED:
            data = self._buffer.read(length)
            return zlib.decompress(data).decode()
        return self._buffer.read(length).decode("utf-8")

    def read_key_value(self):
        handler, _ = self.read_object_id()
        if handler is None:
            return None, None
        key = self.read_value()
        value = handler.deserialise(self)
        return key, value

    def read_length(self):
        length = self._buffer.read(1)
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

        return struct.unpack("<I", self.buffer.read(4))[0]
