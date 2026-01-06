from dataclasses import dataclass


@dataclass
class Config:
    dir: str = "./snapshot"
    min_changes: int = 1
    interval_hours: int = 1
    auto: bool = False
    max_snapshots: int = 4


default_config = Config(min_changes=100, interval_hours=1, auto=False)


class TypeRegistry:
    pass


class Manager:
    pass
