import struct
from binascii import hexlify

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

    def get_view(self):
        return {
            'hash': self.entity_def.hex_digest,
            'name': self.entity_def.name,
            'description': self.entity_def.description,
            'consumes': [],
            'tools': []
        }


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

    @rpc_json
    def do_view(self, payload):
        recipe = _recipe_registry.get(hexlify(payload[1:]))
        return packet_types.CRAFT_VIEW, recipe.get_view()

    def do_exec(self, payload):
        recipe = _recipe_registry.get(hexlify(payload[1:]))
        ent = self.entity.region.spawn(
            recipe.entity_def,
            parent=self.entity.parent,
            spawn_components={
                'Position': dict(
                    x=self.entity.Position.x,
                    y=self.entity.Position.y,
                    vx=self.entity.Position.vx,
                    vy=self.entity.Position.vy
                )
            }
        )

        ent.Position._update()

