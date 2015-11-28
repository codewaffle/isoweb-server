import packet_types
from component.base import BaseComponent, DefinitionComponent
from component.controller import Controller
from network.rpc import rpc_json

_recipe_registry = {}


class CraftRecipe(DefinitionComponent):
    consume = None
    tool = None

    def initialize(self, def_args):
        _recipe_registry[self.entity_def.hex_digest] = self


class CraftingController(Controller):
    def initialize(self):
        self.entity.packet_handlers[packet_types.CRAFT_LIST] = self.do_list
        self.entity.packet_handlers[packet_types.CRAFT_VIEW] = self.do_view
        self.entity.packet_handlers[packet_types.CRAFT_EXEC] = self.do_exec

    @rpc_json
    def do_list(self, payload):
        return packet_types.CRAFT_LIST, [
            (k, v.entity_def.name) for k, v in _recipe_registry.items()
        ]

    def do_view(self, payload):
        pass

    def do_exec(self, payload):
        pass
