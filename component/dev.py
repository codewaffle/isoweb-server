from functools import partial
from math import pi
from random import randint, uniform
from time import clock

from component import BaseComponent
from component.base import component_method, MenuComponent
from component.network import string_replicator
from mathx.vector2 import Vector2


class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 100)'
    }

    @component_method
    def initialize(self):
        self.entity.snapshots[string_replicator(partial(getattr, self.data, 'hit_area'), 'hit_area')] = clock()


class Choppable(MenuComponent):
    @component_method
    def get_menu(self, ent):
        return {
            '!chop': ('Chop with bare hands', self.chop)
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
        for x in range(randint(1, 3)):
            self.island.spawn('log', pos=self.pos + Vector2.random_inside(4.0), rot=uniform(0, pi * 2.0))


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


class Container(MenuComponent):
    @component_method
    def get_menu(self, ent):
        return {
            '!view': ('View contents (noop)', self.view_contents)
        }

    @component_method
    def view_contents(self, ent):
        print ent, 'tried to view contents.'
