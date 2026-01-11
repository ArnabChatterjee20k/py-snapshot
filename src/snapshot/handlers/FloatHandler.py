from ..TypeHandler import TypeHandler
from ..Writer import Writer
from ..Reader import Reader


class FloatHandler(TypeHandler[float]):
    type_identifier = 4
    python_type = float
    is_sequence_type = False

    def serialise(self, writer: Writer, value: float) -> int:
        if not self.can_handle(value):
            raise TypeError("Can handle value")

        return writer.write_value(value)

    def deserialise(self, reader: Reader) -> float:
        return float(reader.read_value())
