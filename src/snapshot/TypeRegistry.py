from .TypeHandler import TypeHandler


class TypeRegistry:
    def __init__(self):
        self._by_types: dict[type, TypeHandler] = {}
        self._by_ids: dict[int, TypeHandler] = {}
        self._sequence_types: set[int] = set()

    def register(self, handler: TypeHandler):
        _type = handler.python_type
        _id = handler.type_identifier

        if not handler.override_previous_entry:
            if _type in self._by_types:
                raise ValueError(f"Handler already registered for type {_type}")

            if _id in self._by_ids:
                raise ValueError(f"Handler already registered for identifier {_id}")

        self._by_types[_type] = handler
        self._by_ids[_id] = handler
        if handler.is_sequence_type:
            self._sequence_types.add(_id)

    def get_handler_by_id(self, id):
        return self._by_ids.get(id)

    def get_handler_by_type(self, datatype: type):
        return self._by_types.get(datatype)

    def is_sequence_type(self, id):
        return id in self._sequence_types


class TypeNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
