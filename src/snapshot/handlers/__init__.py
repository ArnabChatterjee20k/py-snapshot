from ..TypeHandler import TypeHandler


class StringHandler(TypeHandler[str]):
    type_identifier = 1
    python_type = str

    def serialise(self, writer, value: str) -> None:
        pass

    def deserialise(self, reader) -> str:
        pass
