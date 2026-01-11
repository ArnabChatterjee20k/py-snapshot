"""Pytest configuration and fixtures."""

import pytest
from io import BytesIO
from src.snapshot.Writer import Writer
from src.snapshot.Reader import Reader


@pytest.fixture
def buffer():
    """Create a fresh BytesIO buffer for each test."""
    return BytesIO()


@pytest.fixture
def writer(buffer):
    """Create a Writer instance with a buffer."""
    return Writer(buffer=buffer)


@pytest.fixture
def reader(buffer):
    """Create a Reader instance with a buffer."""
    return Reader(buffer=buffer)


@pytest.fixture
def writer_reader_pair():
    """Create a writer and reader sharing the same buffer."""
    buffer = BytesIO()
    writer = Writer(buffer=buffer)
    reader = Reader(buffer=buffer)
    return writer, reader, buffer
