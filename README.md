# py-snapshot

An easy to use python dictionary snapshot generation and saving it.
Major part of https://github.com/ArnabChatterjee20k/pycache

Extracting here for usage in other projects
Use cases -> Backups, saving inmemory states in compressed form

## Features

- **Efficient Serialization**: Compress and serialize Python dictionaries to binary format
- **Type-Aware**: Handles integers, strings, dictionaries, lists, and more with optimized encoding
- **Flexible Storage**: Save to files or work directly with binary buffers/streams
- **Snapshot Management**: Built-in snapshot manager for versioned backups
- **Extensible**: Register custom type handlers for any Python type
- **Compression**: Automatic compression for large string values

## Installation

```bash
uv pip install git+https://github.com/ArnabChatterjee20k/py-snapshot.git

# or

pip install git+https://github.com/ArnabChatterjee20k/py-snapshot.git
```

## Quick Start

### Basic Usage

```python
from src.snapshot import SnapshotManager
from io import BytesIO

# Initialize snapshot manager
manager = SnapshotManager(path="./snapshots")

# Save a dictionary to a file
data = {
    "user_id": 12345,
    "name": "John Doe",
    "settings": {
        "theme": "dark",
        "notifications": True
    },
    "tags": ["python", "compression", "serialization"]
}
manager.dump(data)

# Load the most recent snapshot
loaded_data = manager.load()
print(loaded_data)  # Same as original data
```

### Working with Buffers

```python
from src.snapshot import SnapshotManager
from io import BytesIO

manager = SnapshotManager()

# Write to a buffer (in-memory)
buffer = BytesIO()
data = {"key": "value", "number": 42}
bytes_written = manager.write_to_buffer(data, buffer)

# Read from buffer
buffer.seek(0)
loaded = manager.read_from_buffer(buffer)
assert loaded == data
```

### Direct Writer/Reader Usage

```python
from src.snapshot import Writer, Reader
from io import BytesIO

# Write data
buffer = BytesIO()
writer = Writer(source={"name": "Alice", "age": 30}, buffer=buffer)
writer.write()

# Read data
buffer.seek(0)
reader = Reader(buffer=buffer)
data = reader.read()
print(data)  # {'name': 'Alice', 'age': 30}
```

## Real-World Applications

### 1. Application State Backup

Save application state for crash recovery or checkpointing:

```python
from src.snapshot import SnapshotManager

manager = SnapshotManager(path="./checkpoints")

# Save game state
game_state = {
    "level": 5,
    "score": 12500,
    "inventory": ["sword", "shield", "potion"],
    "player_position": {"x": 100, "y": 200},
    "settings": {"difficulty": "hard", "sound": True}
}
manager.dump(game_state)

# Later, restore from checkpoint
restored_state = manager.load()
```

### 2. Database Cache Snapshots

Create compressed snapshots of frequently accessed data:

```python
from src.snapshot import SnapshotManager
from datetime import datetime

manager = SnapshotManager(path="./cache_snapshots")

# Cache database query results
cache_data = {
    "timestamp": str(datetime.now()),
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ],
    "metadata": {"query": "SELECT * FROM users", "count": 2}
}
manager.dump(cache_data)

# Load specific snapshot by timestamp
target_time = "2024-01-15_10-30-00-000000"
snapshot = manager.load(target_timestamp=target_time)
```

### 3. Configuration Management

Version control for application configurations:

```python
from src.snapshot import SnapshotManager

manager = SnapshotManager(path="./config_backups")

# Save configuration before changes
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "api_keys": {
        "stripe": "sk_live_...",
        "aws": "AKIA..."
    },
    "features": {
        "new_ui": True,
        "beta_features": False
    }
}
manager.dump(config)

# List all configuration snapshots
snapshots = manager.list()
for snapshot in snapshots:
    print(f"Config saved at: {snapshot.name}")

# Restore previous configuration
previous_config = manager.load(target_timestamp="2024-01-15_09-00-00-000000")
```

### 4. Microservice State Persistence

Save state between service restarts:

```python
from src.snapshot import SnapshotManager
from io import BytesIO

manager = SnapshotManager()

# Save service state to buffer for quick access
service_state = {
    "active_connections": 42,
    "processed_requests": 1250,
    "queue": ["task1", "task2", "task3"],
    "metrics": {
        "avg_response_time": 0.125,
        "error_rate": 0.01
    }
}

# Option 1: Save to file
manager.dump(service_state)

# Option 2: Save to buffer for in-memory access
buffer = BytesIO()
manager.write_to_buffer(service_state, buffer)
# Can send buffer over network, store in Redis, etc.
```

### 5. Data Pipeline Checkpoints

Create checkpoints in data processing pipelines:

```python
from src.snapshot import SnapshotManager

manager = SnapshotManager(path="./pipeline_checkpoints")

# Save processing state
pipeline_state = {
    "stage": "transformation",
    "processed_records": 10000,
    "errors": [],
    "output_files": ["output_1.csv", "output_2.csv"],
    "metadata": {
        "start_time": "2024-01-15T10:00:00",
        "source": "data_warehouse"
    }
}
manager.dump(pipeline_state)

# Resume from checkpoint after interruption
checkpoint = manager.load()
if checkpoint["stage"] == "transformation":
    # Resume transformation
    continue_processing(checkpoint)
```

### 6. Session State Management

Store user session data efficiently:

```python
from src.snapshot import SnapshotManager
from io import BytesIO

manager = SnapshotManager()

# Save session to buffer for quick retrieval
session_data = {
    "user_id": "user_12345",
    "cart": [
        {"item_id": 1, "quantity": 2, "price": 29.99},
        {"item_id": 5, "quantity": 1, "price": 49.99}
    ],
    "preferences": {
        "currency": "USD",
        "language": "en",
        "theme": "light"
    },
    "last_activity": "2024-01-15T10:30:00"
}

buffer = BytesIO()
manager.write_to_buffer(session_data, buffer)
# Store buffer.getvalue() in Redis, Memcached, or database
```

## Registering Custom Type Handlers

The library uses a type handler system to serialize/deserialize different Python types. You can register custom handlers for your own types:

### Creating a Custom Handler

```python
from src.snapshot.TypeHandler import TypeHandler
from src.snapshot.Writer import Writer
from src.snapshot.Reader import Reader

class CustomTypeHandler(TypeHandler[YourType]):
    type_identifier = 10  # Unique identifier (must not conflict with existing)
    python_type = YourType
    is_sequence_type = False  # Set to True if it's a collection type

    def serialise(self, writer: Writer, value: YourType) -> int:
        """Serialize your type to bytes."""
        if not self.can_handle(value):
            raise TypeError("Cannot handle this type")
        
        # Write your type's data
        # Example: convert to string and write
        return writer.write_value(str(value))

    def deserialise(self, reader: Reader) -> YourType:
        """Deserialize bytes back to your type."""
        # Read the data and reconstruct your type
        data = reader.read_value()
        return YourType.from_string(data)  # Example
```

### Registering Handlers

```python
from src.snapshot import SnapshotManager
from src.snapshot.handlers import IntHandler, StringHandler

manager = SnapshotManager()

# Register custom handlers
custom_handler = CustomTypeHandler()
manager.register([custom_handler])

# Now you can use your custom type
data = {"custom_field": YourType(...)}
manager.dump(data)
```

### Example: DateTime Handler

```python
from datetime import datetime
from src.snapshot.TypeHandler import TypeHandler
from src.snapshot.Writer import Writer
from src.snapshot.Reader import Reader

class DateTimeHandler(TypeHandler[datetime]):
    type_identifier = 11
    python_type = datetime
    is_sequence_type = False

    def serialise(self, writer: Writer, value: datetime) -> int:
        if not self.can_handle(value):
            raise TypeError("Cannot handle datetime")
        # Serialize as ISO format string
        iso_string = value.isoformat()
        return writer.write_value(iso_string)

    def deserialise(self, reader: Reader) -> datetime:
        iso_string = reader.read_value()
        return datetime.fromisoformat(iso_string)

# Register it
manager = SnapshotManager()
manager.register([DateTimeHandler()])
```

## Snapshot Management

### Listing Snapshots

```python
# List all snapshots (newest first)
snapshots = manager.list()
for snapshot in snapshots:
    print(f"{snapshot.name} - {snapshot.stat().st_mtime}")

# List snapshots closest to a specific timestamp
target = "2024-01-15_12-00-00-000000"
closest = manager.list(target_timestamp=target)
```

### Pruning Old Snapshots

```python
# Remove the oldest snapshot
pruned = manager.prune(max_prune=1)
print(f"Removed {pruned} snapshot(s)")

# Remove a specific snapshot
manager.prune_snapshot("./snapshots/2024-01-15_10-00-00-000000")
```

## Format Specification

The binary format used for serialization:

```
[OBJECT_TYPE]
[KEY_LENGTH]
[KEY_DATA]
[Compressed Length/Original Length]
[ENCODING_MARKER] | if 3 then read the data for compressed length else the original length
[VALUE_ENCODING/DATA]
```

### Encoding Details

Numbers are also written as string, so the Encoder is used to write them to bytes:
- `mask = 3 << 6` => 3 means 11 => so getting a 8bit
- `encoding = mask | encoding` => gives the value
- So we will have something like `11000000`, `11000001`, `11000010`
- Read MSB == 11 => integer encoding => read the LSB

## API Reference

### SnapshotManager

- `__init__(path="./snapshot")` - Initialize with snapshot directory path
- `dump(source: dict)` - Save dictionary to a file with timestamp
- `load(target_timestamp: str = None)` - Load most recent or specific snapshot
- `write_to_buffer(source: dict, buffer: BinaryIO) -> int` - Write to binary buffer
- `read_from_buffer(buffer: BinaryIO) -> dict` - Read from binary buffer
- `list(target_timestamp: str = None)` - List all snapshots
- `prune(max_prune=1)` - Remove oldest snapshots
- `prune_snapshot(snapshot_name: str)` - Remove specific snapshot
- `register(handlers: list[TypeHandler])` - Register custom type handlers

### Writer

- `__init__(source: dict = None, buffer: BinaryIO = None)` - Initialize writer
- `write()` - Write source dictionary to buffer
- `write_key_value(key, value) -> int` - Write a single key-value pair
- `write_value(value) -> int` - Write a value (with compression if beneficial)

### Reader

- `__init__(buffer: BinaryIO = None)` - Initialize reader
- `read() -> dict` - Read complete dictionary from buffer
- `read_key_value() -> tuple` - Read a single key-value pair

## Development

### Running Tests

```bash
# Install dependencies
uv pip install -r pyprojects.toml

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_snapshot.py -v
```

### Project Structure

```
py-snapshot/
├── src/
│   └── snapshot/
│       ├── __init__.py          # Registry initialization
│       ├── Writer.py            # Serialization
│       ├── Reader.py            # Deserialization
│       ├── Snapshot.py          # Snapshot manager
│       ├── TypeHandler.py       # Base handler class
│       ├── TypeRegistry.py      # Handler registry
│       └── handlers/
│           ├── IntHandler.py
│           ├── StringHandler.py
│           ├── DictHandler.py
│           └── ListHandler.py
├── tests/                       # Test suite
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
