from random import random
from isoweb_time import clock
from component import BaseComponent
from component.base import component_method
from mathx.aabb import AABB
from mathx.quadtree import NodeItem
from mathx.vector2 import Vector2
import packet_types


class EntityOb(NodeItem):
    def __init__(self, ent):
        NodeItem.__init__(self)
        self.ent = ent

    def __repr__(self):
        return 'EntityOb({})'.format(repr(self.pos))


_q_aabb = AABB(Vector2(), 1)

class Position(BaseComponent):
    data = {
        'x': 0.,
        'y': 0.,
        'vx': 0.,
        'vy': 0.,
        'r': 1.
    }

    @component_method
    def _update(self):
        # update quadtree position
        ob = self.entity.ob
        ob.aabb.center.x = self.data.x
        ob.aabb.center.y = self.data.y
        ob.update_quadtree()

        # update snapshot
        self.entity.snapshots[self.entity.Position.snapshot] = clock()

    @component_method
    def on_destroy(self):
        self.entity.ob.remove()

    @component_method
    def initialize(self):
        # quadtree junk
        ob = self.entity.ob
        ob.aabb.center.x = self.data.x or random() - 0.5
        ob.aabb.center.y = self.data.y or random() - 0.5
        self.entity.pos = ob.aabb.center
        self.entity.island.quadtree.insert(ob)

        self.entity.snapshots[self.entity.Position.snapshot] = 0

    @component_method
    def snapshot(self):
        return 'Bfffff', (
            packet_types.POSITION_UPDATE,
            self.data.x, self.data.y, self.data.r,
            self.data.vx, self.data.vy
        )

    @component_method
    def teleport(self, x, y=None):
        if y is None and isinstance(x, Vector2):
            self.data.x = x.x
            self.data.y = x.y
        else:
            self.data.x = x
            self.data.y = y

        self._update()

    @component_method
    def find_nearby(self, radius, exclude=None, flags=0, components=None):
        _q_aabb.center.update(self.entity.ob.aabb.center)
        _q_aabb.hwidth = _q_aabb.hheight = radius

        if exclude is None:
            exclude = set()

        if exclude is True:
            exclude = {self.entity}

        return self.entity.island.quadtree.query_aabb_ents(_q_aabb, exclude, flags, components)

    @component_method
    def get_pos(self, copy=False):
        if copy:
            return self.entity.ob.aabb.center.copy()

        return self.entity.ob.aabb.center
