from ..TypeHandler import TypeHandler
from ..Writer import Writer
from ..Reader import Reader


class DictHandler(TypeHandler[dict]):
    type_identifier = 2
    python_type = dict
    is_sequence_type = True

    def serialise(self, writer: Writer, value: dict) -> int:
        if not self.can_handle(value):
            raise TypeError("Can handle value")

        # writing the length of the dict so that over read/write doesnt happens
        written = writer.write_length(len(value))
        for key, value in value.items():
            written += writer.write_key_value(key, value)

        return written

    def deserialise(self, reader: Reader) -> dict:
        result = {}
        for _ in range(reader.read_length()):
            current_pos = reader.buffer.tell()
            try:
                key, value = reader.read_key_value()
                if key == None or value == None:
                    break
                result[key] = value
            except Exception:
                reader.buffer.seek(current_pos)
                break

        return result
