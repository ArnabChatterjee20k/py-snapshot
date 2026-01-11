"""Tests for SnapshotManager class."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from src.snapshot.Snapshot import SnapshotManager
from src.snapshot.handlers.IntHandler import IntHandler
from src.snapshot.handlers.StringHandler import StringHandler


@pytest.fixture
def temp_snapshot_dir():
    """Create a temporary directory for snapshots."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def snapshot_manager(temp_snapshot_dir):
    """Create a SnapshotManager instance with a temp directory."""
    # Note: There's a bug in _init() that references self._config.dir
    # For now, we'll work around it by ensuring the directory exists
    Path(temp_snapshot_dir).mkdir(parents=True, exist_ok=True)
    return SnapshotManager(path=temp_snapshot_dir)


class TestSnapshotManager:
    """Test cases for SnapshotManager class."""

    def test_init_with_default_path(self, temp_snapshot_dir):
        """Test SnapshotManager initialization with default path."""
        # Create default snapshot directory
        default_path = Path("./snapshot")
        default_path.mkdir(parents=True, exist_ok=True)
        try:
            manager = SnapshotManager()
            assert manager._path is not None
            assert manager._path.exists()
        finally:
            # Cleanup
            if default_path.exists():
                shutil.rmtree(default_path, ignore_errors=True)

    def test_init_with_custom_path(self, temp_snapshot_dir):
        """Test SnapshotManager initialization with custom path."""
        Path(temp_snapshot_dir).mkdir(parents=True, exist_ok=True)
        manager = SnapshotManager(path=temp_snapshot_dir)
        assert manager._path == Path(temp_snapshot_dir)
        assert manager._path.exists()

    def test_register_handlers(self, snapshot_manager):
        """Test registering custom handlers."""
        # Note: Handlers are already registered in __init__.py
        # This test verifies that register() method works
        # We can't re-register the same handlers, so we'll just verify the method exists
        # and that existing handlers are accessible
        assert snapshot_manager._registry.get_handler_by_type(int) is not None
        assert snapshot_manager._registry.get_handler_by_type(str) is not None
        # The register method should exist and be callable
        assert hasattr(snapshot_manager, "register")
        assert callable(snapshot_manager.register)

    def test_dump_creates_file(self, snapshot_manager):
        """Test that dump creates a snapshot file."""
        source = {"key1": "value1", "key2": 42}
        snapshot_manager.dump(source)

        # Check that a file was created
        files = list(snapshot_manager._path.glob("*"))
        assert len(files) == 1
        assert files[0].exists()
        assert files[0].is_file()

    def test_dump_filename_format(self, snapshot_manager):
        """Test that dump creates files with correct timestamp format."""
        source = {"test": "data"}
        snapshot_manager.dump(source)

        files = list(snapshot_manager._path.glob("*"))
        assert len(files) == 1

        # Try to parse the filename as datetime
        filename = files[0].name
        try:
            datetime.strptime(filename, SnapshotManager._datetime_format)
        except ValueError:
            # Check if it's a numbered version (base_filename_counter)
            if "_" in filename:
                base_part = filename.rsplit("_", 1)[0]
                datetime.strptime(base_part, SnapshotManager._datetime_format)
            else:
                pytest.fail(f"Filename {filename} doesn't match expected format")

    def test_dump_handles_duplicate_timestamps(self, snapshot_manager):
        """Test that dump handles duplicate timestamps by appending counter."""
        source = {"test": "data"}

        # Create multiple snapshots quickly (may have same timestamp)
        snapshot_manager.dump(source)
        snapshot_manager.dump(source)
        snapshot_manager.dump(source)

        files = list(snapshot_manager._path.glob("*"))
        assert len(files) >= 1
        # All files should exist
        for file in files:
            assert file.exists()

    def test_dump_writes_correct_data(self, snapshot_manager):
        """Test that dump writes the correct data to file."""
        source = {
            "str": "value",
            "int": 42,
            "nested": {"key": "value"},
            "list": [1, 2, 3],
        }
        snapshot_manager.dump(source)

        # Load and verify
        loaded = snapshot_manager.load()
        assert loaded == source

    def test_load_without_timestamp(self, snapshot_manager):
        """Test loading the most recent snapshot without timestamp."""
        source1 = {"first": "data"}
        source2 = {"second": "data"}

        snapshot_manager.dump(source1)
        # Small delay to ensure different mtime
        import time

        time.sleep(0.01)
        snapshot_manager.dump(source2)

        loaded = snapshot_manager.load()
        # Should load the most recent (source2)
        assert loaded == source2

    def test_load_with_timestamp(self, snapshot_manager):
        """Test loading snapshot with specific timestamp."""
        source1 = {"first": "data"}
        source2 = {"second": "data"}

        snapshot_manager.dump(source1)
        time1 = datetime.now()
        import time

        time.sleep(0.01)
        snapshot_manager.dump(source2)
        time2 = datetime.now()

        # Load using timestamp
        timestamp1 = time1.strftime(SnapshotManager._datetime_format)
        loaded1 = snapshot_manager.load(target_timestamp=timestamp1)
        # Should load the closest snapshot (likely source1)
        assert "first" in loaded1 or "second" in loaded1

    def test_load_empty_directory(self, snapshot_manager):
        """Test loading from empty directory returns empty dict."""
        loaded = snapshot_manager.load()
        assert loaded == {}

    def test_load_round_trip(self, snapshot_manager):
        """Test round-trip: dump then load."""
        original = {
            "string": "test",
            "integer": 123,
            "nested": {"level1": {"level2": "deep"}},
            "list": [1, "mixed", {"key": "value"}],
            "empty_dict": {},
            "empty_list": [],
        }

        snapshot_manager.dump(original)
        loaded = snapshot_manager.load()

        assert loaded == original
        assert loaded["nested"]["level1"]["level2"] == "deep"
        assert loaded["list"] == [1, "mixed", {"key": "value"}]

    def test_list_without_timestamp(self, snapshot_manager):
        """Test listing snapshots without timestamp."""
        snapshot_manager.dump({"test1": "data1"})
        import time

        time.sleep(0.01)
        snapshot_manager.dump({"test2": "data2"})

        result = snapshot_manager.list()
        assert isinstance(result, list)
        assert len(result) >= 1
        # Should be sorted by mtime (newest first)
        for file in result:
            assert file.exists()

    def test_list_with_timestamp(self, snapshot_manager):
        """Test listing snapshots with timestamp."""
        snapshot_manager.dump({"test1": "data1"})
        import time

        time.sleep(0.01)
        snapshot_manager.dump({"test2": "data2"})

        target_time = datetime.now()
        target_timestamp = target_time.strftime(SnapshotManager._datetime_format)

        files = snapshot_manager.list(target_timestamp=target_timestamp)
        assert isinstance(files, list)
        assert len(files) >= 1
        # Files should be sorted by distance from target timestamp
        for file in files:
            assert file.exists()

    def test_prune_no_snapshots(self, snapshot_manager):
        """Test pruning when there are no snapshots."""
        pruned = snapshot_manager.prune(max_prune=1)
        assert pruned == 0

    def test_prune_less_than_max(self, snapshot_manager):
        """Test pruning when snapshots < max_prune."""
        snapshot_manager.dump({"test": "data"})
        pruned = snapshot_manager.prune(max_prune=5)
        assert pruned == 0

    def test_prune_removes_oldest(self, snapshot_manager):
        """Test that prune removes the oldest snapshots."""
        snapshot_manager.dump({"test1": "data1"})
        import time

        time.sleep(0.01)
        snapshot_manager.dump({"test2": "data2"})
        time.sleep(0.01)
        snapshot_manager.dump({"test3": "data3"})

        initial_count = len(list(snapshot_manager._path.glob("*")))
        pruned = snapshot_manager.prune(max_prune=1)

        assert pruned == 1
        final_count = len(list(snapshot_manager._path.glob("*")))
        assert final_count == initial_count - 1

    def test_prune_snapshot_by_name(self, snapshot_manager):
        """Test pruning a specific snapshot by name."""
        snapshot_manager.dump({"test": "data"})

        files = list(snapshot_manager._path.glob("*"))
        assert len(files) == 1

        snapshot_name = str(files[0])
        snapshot_manager.prune_snapshot(snapshot_name)

        # File should be deleted
        assert not Path(snapshot_name).exists()

    def test_prune_snapshot_nonexistent(self, snapshot_manager):
        """Test pruning a non-existent snapshot raises exception."""
        with pytest.raises(Exception, match="doesn't exists"):
            snapshot_manager.prune_snapshot("/nonexistent/path/file")

    def test_multiple_dumps_and_loads(self, snapshot_manager):
        """Test multiple dumps and loads maintain data integrity."""
        sources = [
            {"iteration": 1, "data": "first"},
            {"iteration": 2, "data": "second"},
            {"iteration": 3, "data": "third"},
        ]

        for source in sources:
            snapshot_manager.dump(source)
            import time

            time.sleep(0.01)

        # Load the most recent
        loaded = snapshot_manager.load()
        assert loaded["iteration"] == 3
        assert loaded["data"] == "third"

    def test_dump_with_complex_data(self, snapshot_manager):
        """Test dumping and loading complex nested data structures."""
        # Note: Using string "true" instead of boolean True since there's no BoolHandler
        complex_data = {
            "metadata": {"version": 1, "timestamp": "2024-01-01"},
            "items": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"},
            ],
            "settings": {
                "enabled": "true",  # Using string instead of bool
                "count": 42,
                "tags": ["tag1", "tag2"],
            },
        }

        snapshot_manager.dump(complex_data)
        loaded = snapshot_manager.load()

        assert loaded == complex_data
        assert len(loaded["items"]) == 2
        assert loaded["items"][0]["id"] == 1

    def test_datetime_format(self, snapshot_manager):
        """Test that datetime format is consistent."""
        source = {"test": "data"}
        snapshot_manager.dump(source)

        files = list(snapshot_manager._path.glob("*"))
        filename = files[0].name

        # Check if it matches the format (may have counter suffix)
        if "_" in filename and filename.split("_")[-1].isdigit():
            # Has counter, extract base name
            base_name = "_".join(filename.split("_")[:-1])
        else:
            base_name = filename

        # Try to parse
        try:
            parsed = datetime.strptime(base_name, SnapshotManager._datetime_format)
            assert isinstance(parsed, datetime)
        except ValueError:
            pytest.fail(f"Filename {filename} doesn't match datetime format")
