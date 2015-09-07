from functools import partial
from math import pi
from random import uniform
from isoweb_time import clock

from component import BaseComponent
from component.base import component_method, MenuComponent
from component.network import string_replicator, float_replicator
from mathx.vector2 import Vector2


class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 100)'
    }
    exports = ['hit_area']

    @component_method
    def initialize(self):
        self.entity.snapshots[string_replicator(partial(getattr, self.data, 'hit_area'), 'hit_area')] = clock()


class Choppable(MenuComponent):
    data = {
        'label': 'Chop!',
        'output_def': 'log',
        'output_count': 1
    }

    @component_method
    def get_menu(self, ent):
        return {
            'chop': (self.data.label, partial(self.chop, ent))
        }

    @component_method
    def chop(self, chopper):
        chopper.controller.set_queue([
            chopper.controller.move_near_task(self.entity.pos, 0.0),
            (self.do_chop, (chopper,))
        ])

    @component_method
    def do_chop(self, chopper):
        self.entity.destroy()
        for x in range(self.data.output_count):
            self.entity.region.spawn(self.data.output_def, pos=self.entity.pos + Vector2.random_inside(0.2), rot=uniform(0, pi * 2.0))


class TileMap(BaseComponent):
    pass


class Structure(BaseComponent):
    data = {
        'tileset': 'default',
        'size': None,
        'data': None
    }

    exports = ['tileset', 'size', 'data']
