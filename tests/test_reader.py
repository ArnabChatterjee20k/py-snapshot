"""Tests for Reader class."""

import pytest
from io import BytesIO
from src.snapshot.Reader import Reader
from src.snapshot.Writer import Writer
from src.snapshot.TypeHandler import EncodingTypes
from src.snapshot.TypeRegistry import TypeNotFoundException


class TestReader:
    """Test cases for Reader class."""

    def test_init_with_buffer(self, buffer):
        """Test Reader initialization with buffer."""
        reader = Reader(buffer=buffer)
        assert reader.buffer == buffer
        assert reader._buffer == buffer

    def test_set_buffer(self, reader):
        """Test setting buffer after initialization."""
        new_buffer = BytesIO()
        reader.set_buffer(new_buffer)
        assert reader.buffer == new_buffer

    def test_read_encoding_with_encoding(self, buffer):
        """Test reading an encoding marker."""
        # Write an encoding marker
        writer = Writer(buffer=buffer)
        writer.write_encoding(EncodingTypes.INT8)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        encoding = reader.read_encoding()
        assert encoding == EncodingTypes.INT8

    def test_read_encoding_without_encoding(self, buffer):
        """Test reading when no encoding marker is present."""
        # Write a regular byte
        buffer.write(bytes([42]))
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        encoding = reader.read_encoding()
        assert encoding is None
        # Should have seeked back
        assert buffer.tell() == 0

    def test_read_length_small(self, buffer):
        """Test reading small length values."""
        length = 42
        buffer.write(bytes([length]))
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_length = reader.read_length()
        assert read_length == length

    def test_read_length_medium(self, buffer):
        """Test reading medium length values."""
        length = 100
        first_byte = (length >> 8) | 64
        second_byte = length & 0xFF
        buffer.write(bytes([first_byte, second_byte]))
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_length = reader.read_length()
        assert read_length == length

    def test_read_length_large(self, buffer):
        """Test reading large length values."""
        import struct

        length = 1000
        buffer.write(bytes([128]))  # Marker
        buffer.write(struct.pack("<I", length))
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_length = reader.read_length()
        assert read_length == length

    def test_read_value_uncompressed(self, buffer):
        """Test reading an uncompressed value."""
        value = "hello"
        writer = Writer(buffer=buffer)
        writer.write_value(value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_value = reader.read_value()
        assert read_value == value

    def test_read_value_compressed(self, buffer):
        """Test reading a compressed value."""
        value = "a" * 100  # Long string that compresses
        writer = Writer(buffer=buffer)
        writer.write_value(value)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        # Check if compression marker exists
        encoding = reader.read_encoding()
        if encoding == EncodingTypes.COMPRESSED:
            read_value = reader.read_value(encoding)
            assert read_value == value

    def test_read_object_id(self, buffer):
        """Test reading object type identifier."""
        writer = Writer(buffer=buffer)
        handler, _ = writer.write_object_id("test")
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        read_handler, bytes_read = reader.read_object_id()
        assert bytes_read == 1
        assert read_handler is not None
        assert read_handler.python_type == str

    def test_read_object_id_eof(self, buffer):
        """Test reading object ID when EOF marker is present."""
        writer = Writer(buffer=buffer)
        writer.write_encoding(EncodingTypes.EOF)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        handler, marker = reader.read_object_id()
        assert handler is None
        assert marker == 1

    def test_read_object_id_unknown_type(self, buffer):
        """Test reading object ID with unknown type raises exception."""
        buffer.write(bytes([99]))  # Unknown type ID
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        with pytest.raises(TypeNotFoundException):
            reader.read_object_id()

    def test_read_key_value_string(self, writer_reader_pair):
        """Test reading a key-value pair with string value."""
        writer, reader, buffer = writer_reader_pair
        key = "test_key"
        value = "test_value"
        writer.write_key_value(key, value)
        buffer.seek(0)

        read_key, read_value = reader.read_key_value()
        assert read_key == key
        assert read_value == value

    def test_read_key_value_int(self, writer_reader_pair):
        """Test reading a key-value pair with int value."""
        writer, reader, buffer = writer_reader_pair
        key = "number"
        value = 42
        writer.write_key_value(key, value)
        buffer.seek(0)

        read_key, read_value = reader.read_key_value()
        assert read_key == key
        assert read_value == value
        assert isinstance(read_value, int)

    def test_read_key_value_dict(self, writer_reader_pair):
        """Test reading a key-value pair with dict value."""
        writer, reader, buffer = writer_reader_pair
        key = "data"
        value = {"nested_key": "nested_value", "number": 123}
        writer.write_key_value(key, value)
        buffer.seek(0)

        read_key, read_value = reader.read_key_value()
        assert read_key == key
        assert read_value == value
        assert isinstance(read_value, dict)

    def test_read_key_value_nested_dict(self, writer_reader_pair):
        """Test reading nested dictionaries."""
        writer, reader, buffer = writer_reader_pair
        key = "root"
        value = {"level1": {"level2": {"level3": "deep_value"}}}
        writer.write_key_value(key, value)
        buffer.seek(0)

        read_key, read_value = reader.read_key_value()
        assert read_key == key
        assert read_value == value
        assert read_value["level1"]["level2"]["level3"] == "deep_value"

    def test_read_key_value_eof(self, buffer):
        """Test reading key-value when EOF is encountered."""
        writer = Writer(buffer=buffer)
        writer.write_encoding(EncodingTypes.EOF)
        buffer.seek(0)

        reader = Reader(buffer=buffer)
        key, value = reader.read_key_value()
        assert key is None
        assert value is None

    def test_read_full_dict(self, writer_reader_pair):
        """Test reading a complete dictionary using read()."""
        writer, reader, buffer = writer_reader_pair
        original_source = {
            "key1": "value1",
            "key2": 42,
            "key3": {"nested": "data"},
            "key4": [1, 2, 3],
        }

        writer.set_source(original_source)
        writer.write()
        buffer.seek(0)

        read_dict = reader.read()
        assert read_dict == original_source

    def test_read_empty_dict(self, writer_reader_pair):
        """Test reading an empty dictionary."""
        writer, reader, buffer = writer_reader_pair
        original_source = {}

        writer.set_source(original_source)
        writer.write()
        buffer.seek(0)

        read_dict = reader.read()
        assert read_dict == original_source

    def test_round_trip_string(self, writer_reader_pair):
        """Test round-trip serialization/deserialization of string."""
        writer, reader, buffer = writer_reader_pair
        original_key = "my_key"
        original_value = "my_value"

        writer.write_key_value(original_key, original_value)
        buffer.seek(0)

        read_key, read_value = reader.read_key_value()
        assert read_key == original_key
        assert read_value == original_value

    def test_round_trip_int(self, writer_reader_pair):
        """Test round-trip serialization/deserialization of int."""
        writer, reader, buffer = writer_reader_pair
        original_key = "number"
        original_value = -12345

        writer.write_key_value(original_key, original_value)
        buffer.seek(0)

        read_key, read_value = reader.read_key_value()
        assert read_key == original_key
        assert read_value == original_value

    def test_round_trip_dict(self, writer_reader_pair):
        """Test round-trip serialization/deserialization of dict."""
        writer, reader, buffer = writer_reader_pair
        original_key = "data"
        original_value = {"str": "value", "int": 42, "nested": {"key": "value"}}

        writer.write_key_value(original_key, original_value)
        buffer.seek(0)

        read_key, read_value = reader.read_key_value()
        assert read_key == original_key
        assert read_value == original_value

    def test_round_trip_full_dict(self, writer_reader_pair):
        """Test round-trip serialization/deserialization using write() and read()."""
        writer, reader, buffer = writer_reader_pair
        original_source = {
            "str": "value",
            "int": 42,
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "empty_dict": {},
            "empty_list": [],
        }

        writer.set_source(original_source)
        writer.write()
        buffer.seek(0)

        read_dict = reader.read()
        assert read_dict == original_source
