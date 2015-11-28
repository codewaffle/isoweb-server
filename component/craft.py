import packet_types
from component.base import BaseComponent
from component.controller import Controller
from network.rpc import rpc_json

_craftable_registry = {}


class Craftable(BaseComponent):
    recipe = None

    def initialize(self):
        pass

    @classmethod
    def process_args(cls, args):
        return super().process_args(args)


class CraftingController(Controller):
    def initialize(self):
        self.entity.packet_handlers[packet_types.CRAFT_LIST] = self.do_list
        self.entity.packet_handlers[packet_types.CRAFT_VIEW] = self.do_view
        self.entity.packet_handlers[packet_types.CRAFT_EXEC] = self.do_exec

    @rpc_json
    def do_list(self, payload):
        return packet_types.CRAFT_LIST, [
            # list of things the player can craft, somehow..
        ]

    def do_view(self, payload):
        pass

    def do_exec(self, payload):
        pass
