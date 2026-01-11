"""Tests for type handlers."""

import pytest
from io import BytesIO
from src.snapshot.Writer import Writer
from src.snapshot.Reader import Reader
from src.snapshot.handlers.IntHandler import IntHandler
from src.snapshot.handlers.StringHandler import StringHandler
from src.snapshot.handlers.DictHandler import DictHandler
from src.snapshot.handlers.ListHandler import ListHandler
from src.snapshot.TypeHandler import EncodingTypes


class TestIntHandler:
    """Test cases for IntHandler."""

    def test_type_identifier(self):
        """Test type identifier is correct."""
        handler = IntHandler()
        assert handler.type_identifier == 1

    def test_python_type(self):
        """Test python_type is correct."""
        handler = IntHandler()
        assert handler.python_type == int

    def test_can_handle_int(self):
        """Test can_handle returns True for int."""
        handler = IntHandler()
        assert handler.can_handle(42) is True
        assert handler.can_handle(-100) is True
        assert handler.can_handle(0) is True

    def test_can_handle_non_int(self):
        """Test can_handle returns False for non-int."""
        handler = IntHandler()
        assert handler.can_handle("42") is False
        assert handler.can_handle(42.0) is False
        assert handler.can_handle([1, 2, 3]) is False

    def test_serialise_int8(self, buffer):
        """Test serializing INT8 value."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        value = 42
        bytes_written = handler.serialise(writer, value)
        assert bytes_written >= 2
        buffer.seek(0)
        encoding_byte = buffer.read(1)[0]
        assert (encoding_byte >> 6) == 3
        encoding = EncodingTypes(encoding_byte & 0x3F)
        assert encoding == EncodingTypes.INT8

    def test_serialise_int16(self, buffer):
        """Test serializing INT16 value."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        value = 1000
        bytes_written = handler.serialise(writer, value)
        assert bytes_written >= 3
        buffer.seek(0)
        encoding_byte = buffer.read(1)[0]
        encoding = EncodingTypes(encoding_byte & 0x3F)
        assert encoding == EncodingTypes.INT16

    def test_serialise_int32(self, buffer):
        """Test serializing INT32 value."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        value = 100000
        bytes_written = handler.serialise(writer, value)
        assert bytes_written >= 5
        buffer.seek(0)
        encoding_byte = buffer.read(1)[0]
        encoding = EncodingTypes(encoding_byte & 0x3F)
        assert encoding == EncodingTypes.INT32

    def test_serialise_large_int(self, buffer):
        """Test serializing large int that uses string encoding."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        value = 12345678901234567890  # Very large number
        bytes_written = handler.serialise(writer, value)
        assert bytes_written > 0

    def test_deserialise_int8(self, buffer):
        """Test deserializing INT8 value."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        original_value = 42
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value
        assert isinstance(read_value, int)

    def test_deserialise_int16(self, buffer):
        """Test deserializing INT16 value."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        original_value = 1000
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_deserialise_int32(self, buffer):
        """Test deserializing INT32 value."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        original_value = 100000
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_round_trip_negative_int(self, buffer):
        """Test round-trip with negative integers."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        original_value = -42
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_serialise_invalid_type(self, buffer):
        """Test serializing invalid type raises exception."""
        handler = IntHandler()
        writer = Writer(buffer=buffer)
        with pytest.raises(Exception, match="Can't handle"):
            handler.serialise(writer, "not an int")


class TestStringHandler:
    """Test cases for StringHandler."""

    def test_type_identifier(self):
        """Test type identifier is correct."""
        handler = StringHandler()
        assert handler.type_identifier == 3

    def test_python_type(self):
        """Test python_type is correct."""
        handler = StringHandler()
        assert handler.python_type == str

    def test_can_handle_string(self):
        """Test can_handle returns True for str."""
        handler = StringHandler()
        assert handler.can_handle("hello") is True
        assert handler.can_handle("") is True

    def test_can_handle_non_string(self):
        """Test can_handle returns False for non-str."""
        handler = StringHandler()
        assert handler.can_handle(42) is False
        assert handler.can_handle(["a", "b"]) is False

    def test_serialise_string(self, buffer):
        """Test serializing string value."""
        handler = StringHandler()
        writer = Writer(buffer=buffer)
        value = "hello world"
        bytes_written = handler.serialise(writer, value)
        assert bytes_written > 0

    def test_deserialise_string(self, buffer):
        """Test deserializing string value."""
        handler = StringHandler()
        writer = Writer(buffer=buffer)
        original_value = "hello world"
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value
        assert isinstance(read_value, str)

    def test_round_trip_empty_string(self, buffer):
        """Test round-trip with empty string."""
        handler = StringHandler()
        writer = Writer(buffer=buffer)
        original_value = ""
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_round_trip_unicode_string(self, buffer):
        """Test round-trip with unicode string."""
        handler = StringHandler()
        writer = Writer(buffer=buffer)
        original_value = "Hello 世界 🌍"
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_serialise_invalid_type(self, buffer):
        """Test serializing invalid type raises exception."""
        handler = StringHandler()
        writer = Writer(buffer=buffer)
        with pytest.raises(TypeError, match="Can handle value"):
            handler.serialise(writer, 42)


class TestDictHandler:
    """Test cases for DictHandler."""

    def test_type_identifier(self):
        """Test type identifier is correct."""
        handler = DictHandler()
        assert handler.type_identifier == 2

    def test_python_type(self):
        """Test python_type is correct."""
        handler = DictHandler()
        assert handler.python_type == dict

    def test_is_sequence_type(self):
        """Test is_sequence_type is True."""
        handler = DictHandler()
        assert handler.is_sequence_type is True

    def test_can_handle_dict(self):
        """Test can_handle returns True for dict."""
        handler = DictHandler()
        assert handler.can_handle({}) is True
        assert handler.can_handle({"key": "value"}) is True

    def test_can_handle_non_dict(self):
        """Test can_handle returns False for non-dict."""
        handler = DictHandler()
        assert handler.can_handle([]) is False
        assert handler.can_handle("dict") is False

    def test_serialise_empty_dict(self, buffer):
        """Test serializing empty dictionary."""
        handler = DictHandler()
        writer = Writer(buffer=buffer)
        value = {}
        # data type and length will be written
        bytes_written = handler.serialise(writer, value)
        assert bytes_written == 1

    def test_serialise_dict(self, buffer):
        """Test serializing dictionary."""
        handler = DictHandler()
        writer = Writer(buffer=buffer)
        value = {"key1": "value1", "key2": 42}
        bytes_written = handler.serialise(writer, value)
        assert bytes_written > 0

    def test_deserialise_empty_dict(self, buffer):
        """Test deserializing empty dictionary."""
        handler = DictHandler()
        writer = Writer(buffer=buffer)
        original_value = {}
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_deserialise_dict(self, buffer):
        """Test deserializing dictionary."""
        handler = DictHandler()
        writer = Writer(buffer=buffer)
        original_value = {"key1": "value1", "key2": 42}
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_round_trip_nested_dict(self, buffer):
        """Test round-trip with nested dictionaries."""
        handler = DictHandler()
        writer = Writer(buffer=buffer)
        original_value = {"level1": {"level2": {"level3": "deep"}}}
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value
        assert read_value["level1"]["level2"]["level3"] == "deep"

    def test_round_trip_mixed_types(self, buffer):
        """Test round-trip with mixed value types."""
        handler = DictHandler()
        writer = Writer(buffer=buffer)
        original_value = {
            "str": "value",
            "int": 42,
            "nested": {"key": "value"},
            "empty": {},
        }
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_serialise_invalid_type(self, buffer):
        """Test serializing invalid type raises exception."""
        handler = DictHandler()
        writer = Writer(buffer=buffer)
        with pytest.raises(TypeError, match="Can handle value"):
            handler.serialise(writer, "not a dict")


class TestListHandler:
    """Test cases for ListHandler."""

    def test_type_identifier(self):
        """Test type identifier is correct."""
        handler = ListHandler()
        assert handler.type_identifier == 4

    def test_python_type(self):
        """Test python_type is correct."""
        handler = ListHandler()
        assert handler.python_type == list

    def test_can_handle_list(self):
        """Test can_handle returns True for list."""
        handler = ListHandler()
        assert handler.can_handle([]) is True
        assert handler.can_handle([1, 2, 3]) is True

    def test_can_handle_non_list(self):
        """Test can_handle returns False for non-list."""
        handler = ListHandler()
        assert handler.can_handle({}) is False
        assert handler.can_handle("list") is False

    def test_serialise_empty_list(self, buffer):
        """Test serializing empty list."""
        handler = ListHandler()
        writer = Writer(buffer=buffer)
        value = []
        bytes_written = handler.serialise(writer, value)
        # data type and length will be written
        assert bytes_written == 1

    def test_serialise_list(self, buffer):
        """Test serializing list."""
        handler = ListHandler()
        writer = Writer(buffer=buffer)
        value = ["item1", "item2", 42]
        bytes_written = handler.serialise(writer, value)
        assert bytes_written > 0

    def test_deserialise_list(self, buffer):
        """Test deserializing list."""
        handler = ListHandler()
        writer = Writer(buffer=buffer)
        original_value = ["item1", "item2", 42]
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value
        assert isinstance(read_value, list)

    def test_round_trip_mixed_list(self, buffer):
        """Test round-trip with mixed type list."""
        handler = ListHandler()
        writer = Writer(buffer=buffer)
        original_value = ["string", 42, {"key": "value"}]
        handler.serialise(writer, original_value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = handler.deserialise(reader)
        assert read_value == original_value

    def test_serialise_invalid_type(self, buffer):
        """Test serializing invalid type raises exception."""
        handler = ListHandler()
        writer = Writer(buffer=buffer)
        with pytest.raises(TypeError, match="Can't handle"):
            handler.serialise(writer, "not a list")
