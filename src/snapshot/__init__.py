from .TypeRegistry import TypeRegistry
from .handlers import IntHandler, DictHandler, StringHandler

registry = TypeRegistry()
registry.register(IntHandler())
registry.register(DictHandler())
registry.register(StringHandler())
