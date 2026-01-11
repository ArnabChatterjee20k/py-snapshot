from ..TypeHandler import TypeHandler
from ..Writer import Writer
from ..Reader import Reader


class StringHandler(TypeHandler[str]):
    type_identifier = 3
    python_type = str
    is_sequence_type = False

    def serialise(self, writer: Writer, value: str) -> int:
        if not self.can_handle(value):
            raise TypeError("Can handle value")

        return writer.write_value(value)

    def deserialise(self, reader: Reader) -> str:
        return reader.read_value()
