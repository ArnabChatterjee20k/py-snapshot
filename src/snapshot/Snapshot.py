from pathlib import Path
from datetime import datetime
from typing import BinaryIO
import os
from .Reader import Reader
from .Writer import Writer
from .TypeHandler import TypeHandler


class SnapshotManager:
    _datetime_format = "%Y-%m-%d_%H-%M-%S-%f"

    def __init__(self, path="./snapshot"):
        from . import registry

        self._registry = registry
        self._path = Path(path)
        self._init()

    def register(self, handlers: list[TypeHandler]):
        self._registry.register(handlers)

    def dump(self, source: dict):
        now = datetime.now()
        base_filename = now.strftime(self._datetime_format)
        path = self._path / base_filename

        counter = 0
        while path.exists():
            counter += 1
            unique_filename = f"{base_filename}_{counter}"
            path = self._path / unique_filename

        with open(path, "wb") as f:
            Writer(source, f).write()
            f.flush()
            os.fsync(f.fileno())

    def load(self, target_timestamp: str = None):
        files = list(self._path.glob("*"))
        if not files:
            return {}

        if not target_timestamp:
            snapshot = max(files, key=lambda f: f.stat().st_mtime)
        else:
            # find the timestamp snapshot to target timestamp
            target = datetime.strptime(target_timestamp, self._datetime_format)

            snapshot = min(
                files,
                key=lambda f: abs(
                    target - datetime.strptime(f.name, self._datetime_format)
                ),
            )

        with open(snapshot, "rb") as f:
            reader = Reader(f)
            data = reader.read()
            return data if data else {}

    def list(self, target_timestamp: str = None):
        files = list(self._path.glob("*"))
        if not files:
            return []
        if not target_timestamp:
            # If no target timestamp, return all files sorted by mtime
            return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        target = datetime.strptime(target_timestamp, self._datetime_format)
        return sorted(
            files,
            key=lambda f: abs(
                target - datetime.strptime(f.name, self._datetime_format)
            ),
        )

    def prune(self, max_prune=1):
        snapshots = list(self._path.glob("*"))
        if len(snapshots) < max_prune:
            return 0
        snapshots.sort(key=lambda f: (f.stat().st_mtime, f.name), reverse=True)
        pruned = 0
        for old_snapshot in snapshots[:max_prune]:
            try:
                old_snapshot.unlink()
                pruned += 1
            except Exception as e:
                print(f"Could not prune snapshot {old_snapshot}: {e}")
        return pruned

    def prune_snapshot(self, snapshot_name: str):
        path = Path(snapshot_name)
        if not path.exists():
            raise Exception(f"{snapshot_name} doesn't exists")
        path.unlink()

    def write_to_buffer(self, source: dict, buffer: BinaryIO) -> int:
        writer = Writer(source, buffer)
        writer.write()
        buffer.flush()
        if hasattr(buffer, "tell"):
            return buffer.tell()
        return 0

    def read_from_buffer(self, buffer: BinaryIO) -> dict:
        if hasattr(buffer, "seek"):
            buffer.seek(0)
        reader = Reader(buffer)
        data = reader.read()
        return data if data else {}

    def _init(self):
        path = self._path
        if not path.exists():
            path.mkdir(parents=True)
        elif not path.is_dir():
            raise TypeError("The path needs to be a directory")
