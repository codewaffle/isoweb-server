from functools import partial
from math import pi
from random import uniform
from isoweb_time import clock

from component import BaseComponent
from component.base import component_method, MenuComponent
from component.network import string_replicator, float_replicator
from pymunk import Body, moment_for_circle, Circle
from pymunk.vec2d import Vec2d


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
    def initialize(self):
        self.initialize_menu()

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
            self.region.spawn(self.data.output_def, pos=self.pos + Vec2d(), rot=uniform(0, pi * 2.0))


class TileMap(BaseComponent):
    pass


class Physics(BaseComponent):
    data = {
        'mass': 1.0,
        'volume': 1.0,
        'radius': 1.0
    }

    @component_method
    def init_physics(self):
        body = self.data._body = Body(
            mass=self.data.mass,
            moment=self.compute_moment()
        )
        shape = self.data._shape = self.compute_shape(body)
        self.entity.region.space.add(body, shape)

    @component_method
    def compute_moment(self):
        return moment_for_circle(self.data.mass, 0, self.data.radius)

    @component_method
    def compute_shape(self, body):
        return Circle(body, self.data.radius)

    @component_method
    def get_position(self):
        return self.data._body.position

    @component_method
    def initialize(self):
        self.init_physics()


class PolygonPhysics(BaseComponent):
    pass


class Structure(BaseComponent):
    data = {
        'tileset': 'default',
        'size': None,
        'data': None
    }

    exports = ['tileset', 'size', 'data']

    @component_method
    def initialize(self):
        pass