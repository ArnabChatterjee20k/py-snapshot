import struct
from ..TypeHandler import TypeHandler, EncodingTypes
from ..Writer import Writer


class IntHandler(TypeHandler[int]):
    type_identifier = 1
    python_type = int

    def serialise(self, writer: Writer, value: int) -> int:
        original_length = len(str(value).encode("utf-8"))
        if original_length <= 11:
            if -128 <= value <= 127:
                self._write_encoding(EncodingTypes.INT8)
                self.buffer.write(struct.pack("<b", value))
                return 2
            elif -32768 <= value <= 32767:
                self._write_encoding(EncodingTypes.INT16)
                self.buffer.write(struct.pack("<h", value))
                return 3
            elif -2147483648 <= value <= 2147483647:
                self._write_encoding(EncodingTypes.INT32)
                self.buffer.write(struct.pack("<i", value))
                return 5

        return writer.write_value(value)

    def deserialise(self, reader) -> int:
        return reader.read_int32()
