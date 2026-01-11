"""Tests for Writer class."""

import pytest
from io import BytesIO
from src.snapshot.Writer import Writer
from src.snapshot.TypeHandler import EncodingTypes, VariableLengthEncodingMarkers
from src.snapshot.TypeRegistry import TypeNotFoundException


class TestWriter:
    """Test cases for Writer class."""

    def test_init_with_buffer(self, buffer):
        """Test Writer initialization with buffer."""
        writer = Writer(buffer=buffer)
        assert writer.buffer == buffer
        assert writer._buffer == buffer

    def test_init_with_source_and_buffer(self, buffer):
        """Test Writer initialization with source and buffer."""
        source = {"key": "value"}
        writer = Writer(source=source, buffer=buffer)
        assert writer._source == source
        assert writer.buffer == buffer

    def test_set_buffer(self, writer):
        """Test setting buffer after initialization."""
        new_buffer = BytesIO()
        writer.set_buffer(new_buffer)
        assert writer.buffer == new_buffer

    def test_set_source(self, writer):
        """Test setting source after initialization."""
        source = {"test": "data"}
        writer.set_source(source)
        assert writer._source == source

    def test_write_encoding(self, writer):
        """Test writing encoding markers."""
        writer.write_encoding(EncodingTypes.INT8)
        writer.buffer.seek(0)
        byte = writer.buffer.read(1)[0]
        # Encoding should have prefix 11 (3 << 6)
        assert (byte >> 6) == 3
        assert (byte & 0x3F) == EncodingTypes.INT8.value

    def test_write_length_small(self, writer):
        """Test writing small length values (<= 63)."""
        length = 42
        bytes_written = writer.write_length(length)
        assert bytes_written == 1
        writer.buffer.seek(0)
        assert writer.buffer.read(1)[0] == length

    def test_write_length_medium(self, writer):
        """Test writing medium length values (64-127)."""
        length = 100
        bytes_written = writer.write_length(length)
        assert bytes_written == 2
        writer.buffer.seek(0)
        first_byte = writer.buffer.read(1)[0]
        second_byte = writer.buffer.read(1)[0]
        assert (first_byte & 0x3F) == (length >> 8)
        assert second_byte == (length & 0xFF)

    def test_write_length_large(self, writer):
        """Test writing large length values (> 127)."""
        length = 1000
        bytes_written = writer.write_length(length)
        assert bytes_written == 5
        writer.buffer.seek(0)
        marker = writer.buffer.read(1)[0]
        assert marker == VariableLengthEncodingMarkers.THIRTY_TWO_BIT_ENCODING.value
        import struct

        length_bytes = writer.buffer.read(4)
        assert struct.unpack("<I", length_bytes)[0] == length

    def test_write_value_short_string(self, writer):
        """Test writing a short string value (no compression)."""
        value = "hello"
        bytes_written = writer.write_value(value)
        assert bytes_written > 0
        writer.buffer.seek(0)
        # Should have length + data
        length = writer.buffer.read(1)[0]
        assert length == len(value.encode("utf-8"))
        data = writer.buffer.read(length).decode("utf-8")
        assert data == value

    def test_write_value_long_string_compression(self, writer):
        """Test writing a long string that gets compressed."""
        value = "a" * 100  # Long string that should compress
        bytes_written = writer.write_value(value)
        assert bytes_written > 0
        writer.buffer.seek(0)
        # Check for compression marker
        encoding_byte = writer.buffer.read(1)[0]
        if (encoding_byte >> 6) == 3:
            # Compressed
            encoding = EncodingTypes(encoding_byte & 0x3F)
            assert encoding == EncodingTypes.COMPRESSED

    def test_write_key_value_string(self, writer):
        """Test writing a key-value pair with string value."""
        key = "test_key"
        value = "test_value"
        bytes_written = writer.write_key_value(key, value)
        assert bytes_written > 0
        # Verify structure: type_id + key_length + key_data + value_data
        writer.buffer.seek(0)
        type_id = writer.buffer.read(1)[0]
        assert type_id == 3  # StringHandler type identifier

    def test_write_key_value_int(self, writer):
        """Test writing a key-value pair with int value."""
        key = "number"
        value = 42
        bytes_written = writer.write_key_value(key, value)
        assert bytes_written > 0
        writer.buffer.seek(0)
        type_id = writer.buffer.read(1)[0]
        assert type_id == 1  # IntHandler type identifier

    def test_write_key_value_dict(self, writer):
        """Test writing a key-value pair with dict value."""
        key = "data"
        value = {"nested": "value"}
        bytes_written = writer.write_key_value(key, value)
        assert bytes_written > 0
        writer.buffer.seek(0)
        type_id = writer.buffer.read(1)[0]
        assert type_id == 2  # DictHandler type identifier

    def test_write_key_value_unknown_type(self, writer):
        """Test writing with unknown type raises exception."""
        key = "test"
        value = set([1, 2, 3])  # Set type not registered
        with pytest.raises(TypeNotFoundException):
            writer.write_key_value(key, value)

    def test_write_full_dict(self, writer):
        """Test writing a complete dictionary."""
        source = {"key1": "value1", "key2": 42, "key3": {"nested": "data"}}
        writer.set_source(source)
        writer.write()
        writer.buffer.seek(0)
        # Should have length + key-value pairs + EOF
        length = writer.buffer.read(1)[0]
        assert length == len(source)

    def test_write_object_id(self, writer):
        """Test write_object_id method."""
        value = "test"
        handler, bytes_written = writer.write_object_id(value)
        assert bytes_written == 1
        assert handler is not None
        assert handler.python_type == str
        writer.buffer.seek(0)
        type_id = writer.buffer.read(1)[0]
        assert type_id == handler.type_identifier

    def test_write_object_id_unknown_type(self, writer):
        """Test write_object_id with unknown type raises exception."""
        value = set([1, 2, 3])
        with pytest.raises(TypeNotFoundException):
            writer.write_object_id(value)
