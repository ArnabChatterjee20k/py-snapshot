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
            object_type_handler, byte_written = writer.write_object_id(item)
            written += byte_written
            written += object_type_handler.serialise(writer, item)
        return written

    def deserialise(self, reader: Reader) -> list:
        results = []
        while True:
            current_pos = reader.buffer.tell()
            try:
                object_type_handler, _ = reader.read_object_id()
                value = object_type_handler.deserialise(reader)
                if not value:
                    break
                results.append(value)
            except Exception:
                reader.buffer.seek(current_pos)
                break

        return results
