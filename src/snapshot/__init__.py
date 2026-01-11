from .TypeRegistry import TypeRegistry
from .handlers import IntHandler, DictHandler, StringHandler, ListHandler

registry = TypeRegistry()
registry.register([IntHandler(), DictHandler(), StringHandler(), ListHandler()])
