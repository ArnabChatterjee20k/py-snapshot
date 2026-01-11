from ..TypeHandler import TypeHandler
from ..Writer import Writer
from ..Reader import Reader


class ListHandler(TypeHandler[list]):
    type_identifier = 4
    python_type = list
    is_sequence_type = False

    def serialise(self, writer: Writer, value: list) -> int:
        if not self.can_handle(value):
            raise TypeError("Can't handle value")

        written = 0
        for item in value:
            written += writer.write_value(item)
        return written

    def deserialise(self, reader: Reader) -> list:
        results = []
        while True:
            current_pos = reader.buffer.tell()
            try:
                value = reader.read_value()
                if not value:
                    break
                results.append(value)
            except Exception:
                reader.buffer.seek(current_pos)
                break

        return results
