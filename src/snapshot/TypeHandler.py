from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

T = TypeVar("T")

class TypeHandler(ABC, Generic[T]):
    type_identifier: int
    is_sequence_type: bool = False
    python_type: Type[T]
    override_previous_entry: bool = False

    def can_handle(self, value: object) -> bool:
        return isinstance(value, self.python_type)
    
    @abstractmethod
    def serialise(self, writer, value:T) -> None:
        pass

    @abstractmethod
    def deserialise(self, reader) -> T:
        pass
