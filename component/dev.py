from functools import partial
from math import pi
from random import randint, uniform
from time import clock

from component import BaseComponent
from component.base import component_method, MenuComponent
from component.network import string_replicator, float_replicator
from mathx.vector2 import Vector2


class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 100)'
    }

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
            'chop': (self.data.label, self.chop)
        }

    @component_method
    def chop(self, chopper):
        chopper.controller.set_queue([
            chopper.controller.move_near_task(self.entity.pos, 3),
            (self.do_chop, (chopper,))
        ])

    @component_method
    def do_chop(self, chopper):
        self.entity.destroy()
        for x in range(self.data.output_count):
            self.island.spawn(self.data.output_def, pos=self.pos + Vector2.random_inside(4.0), rot=uniform(0, pi * 2.0))

class Dragger(BaseComponent):
    @component_method
    def initialize(self):
        self.cache.update({
            'contribution': Vector2(),
            'draggable': None
        })

    @component_method
    def get_drag_force(self):
        return 5.0


class TileMap(BaseComponent):
    pass





class Physical(BaseComponent):
    data = {
        'mass': 1.0,
        'volume': 1.0
    }

    @component_method
    def initialize(self):
        self.entity.snapshots[float_replicator(partial(getattr, self.data, 'mass'), 'mass')] = 0
        self.entity.snapshots[float_replicator(partial(getattr, self.data, 'volume'), 'volume')] = 0
