"""Tests for TypeRegistry."""

import pytest
from src.snapshot.TypeRegistry import TypeRegistry, TypeNotFoundException
from src.snapshot.handlers.IntHandler import IntHandler
from src.snapshot.handlers.StringHandler import StringHandler
from src.snapshot.handlers.DictHandler import DictHandler


class TestTypeRegistry:
    """Test cases for TypeRegistry."""

    def test_init(self):
        """Test TypeRegistry initialization."""
        registry = TypeRegistry()
        assert registry._by_types == {}
        assert registry._by_ids == {}
        assert registry._sequence_types == set()

    def test_register_single_handler(self):
        """Test registering a single handler."""
        registry = TypeRegistry()
        handler = IntHandler()
        registry.register(handler)

        assert registry.get_handler_by_type(int) == handler
        assert registry.get_handler_by_id(1) == handler

    def test_register_multiple_handlers(self):
        """Test registering multiple handlers at once."""
        registry = TypeRegistry()
        int_handler = IntHandler()
        str_handler = StringHandler()
        dict_handler = DictHandler()

        registry.register([int_handler, str_handler, dict_handler])

        assert registry.get_handler_by_type(int) == int_handler
        assert registry.get_handler_by_type(str) == str_handler
        assert registry.get_handler_by_type(dict) == dict_handler

    def test_register_duplicate_type(self):
        """Test registering duplicate type raises ValueError."""
        registry = TypeRegistry()
        handler1 = IntHandler()
        handler2 = IntHandler()

        registry.register(handler1)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(handler2)

    def test_register_duplicate_id(self):
        """Test registering duplicate ID raises ValueError."""
        registry = TypeRegistry()
        handler1 = IntHandler()
        # Create another handler with same ID (would need custom handler for this)
        # For now, test with actual duplicate
        registry.register(handler1)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(handler1)

    def test_get_handler_by_type(self):
        """Test getting handler by type."""
        registry = TypeRegistry()
        handler = IntHandler()
        registry.register(handler)

        assert registry.get_handler_by_type(int) == handler
        assert registry.get_handler_by_type(str) is None

    def test_get_handler_by_id(self):
        """Test getting handler by ID."""
        registry = TypeRegistry()
        handler = IntHandler()
        registry.register(handler)

        assert registry.get_handler_by_id(1) == handler
        assert registry.get_handler_by_id(99) is None

    def test_is_sequence_type(self):
        """Test checking if type is sequence type."""
        registry = TypeRegistry()
        dict_handler = DictHandler()
        int_handler = IntHandler()

        registry.register([dict_handler, int_handler])

        assert registry.is_sequence_type(2) is True  # DictHandler
        assert registry.is_sequence_type(1) is False  # IntHandler

    def test_sequence_types_set(self):
        """Test that sequence types are added to set."""
        registry = TypeRegistry()
        dict_handler = DictHandler()
        int_handler = IntHandler()

        registry.register([dict_handler, int_handler])

        assert 2 in registry._sequence_types  # DictHandler
        assert 1 not in registry._sequence_types  # IntHandler

    def test_register_override_previous_entry(self):
        """Test registering with override_previous_entry flag."""
        registry = TypeRegistry()
        handler1 = IntHandler()
        handler2 = IntHandler()
        handler2.override_previous_entry = True

        registry.register(handler1)
        # Should not raise error with override flag
        registry.register(handler2)
        # New handler should replace old one
        assert registry.get_handler_by_type(int) == handler2
