import struct
from ..TypeHandler import TypeHandler, EncodingTypes
from ..Writer import Writer
from ..Reader import Reader


class IntHandler(TypeHandler[int]):
    type_identifier = 1
    python_type = int

    def serialise(self, writer: Writer, value: int) -> int:
        if not self.can_handle(value):
            raise Exception("Can't handle the type")
        original_length = len(str(value).encode("utf-8"))
        if original_length <= 11:
            if -128 <= value <= 127:
                writer.write_encoding(EncodingTypes.INT8)
                writer.buffer.write(struct.pack("<b", value))
                return 2
            elif -32768 <= value <= 32767:
                writer.write_encoding(EncodingTypes.INT16)
                writer.buffer.write(struct.pack("<h", value))
                return 3
            elif -2147483648 <= value <= 2147483647:
                writer.write_encoding(EncodingTypes.INT32)
                writer.buffer.write(struct.pack("<i", value))
                return 5

        return writer.write_value(value)

    def deserialise(self, reader: Reader) -> int:
        encoding = reader.read_encoding()
        if encoding == EncodingTypes.INT8:
            return struct.unpack("<b", reader.buffer.read(1))[0]

        elif encoding == EncodingTypes.INT16:
            return struct.unpack("<h", reader.buffer.read(2))[0]

        elif encoding == EncodingTypes.INT32:
            return struct.unpack("<i", reader.buffer.read(4))[0]

        return reader.read_value(encoding)
