from .TypeHandler import TypeHandler


class TypeRegistry:
    def __init__(self):
        self._by_types: dict[type, TypeHandler] = {}
        self._by_ids: dict[int, TypeHandler] = {}
        self._sequence_types: list[int] = []

    def register(self, handler: TypeHandler):
        _type = handler.python_type
        _id = handler.type_identifier
        _is_sequence = []

        if not handler.override_previous_entry:
            if _type in self._by_types:
                raise ValueError(f"Handler already registered for type {_type}")

            if _id in self._by_ids:
                raise ValueError(f"Handler already registered for identifier {_id}")

        self._by_types[_type] = handler
        self._by_ids[_id] = handler
        self._sequence_types.append(_id)
