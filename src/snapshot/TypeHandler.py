from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar
from enum import Enum

T = TypeVar("T")


class TypeHandler(ABC, Generic[T]):
    type_identifier: int
    is_sequence_type: bool = False
    python_type: Type[T]
    override_previous_entry: bool = False

    def can_handle(self, value: object) -> bool:
        return isinstance(value, self.python_type)

    @abstractmethod
    def serialise(self, writer, value: T) -> None:
        pass

    @abstractmethod
    def deserialise(self, reader) -> T:
        pass


ALL_SET_MARKER = 0xFF


class VariableLengthEncodingMarkers(Enum):
    SIX_BIT_ENCODING = 63
    FORTEEN_BIT_ENCODING = 127
    THIRTY_TWO_BIT_ENCODING = 0x80  # 128


class EncodingTypes(Enum):
    INT8 = 0
    INT16 = 1
    INT32 = 2
    COMPRESSED = 3
    EOF = 0x00
