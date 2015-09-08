from random import random
from isoweb_time import clock
from component import BaseComponent
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
    x = 0.
    y = 0.
    vx = 0.
    vy = 0.

    w = 1.
    h = 1.

    r = 0.  # rotation

    parent = None
    _parent = None

    persists = ['x', 'y', 'vx', 'vy', 'w', 'h', 'r', 'parent']

    def _update(self):
        # update quadtree position
        ob = self.entity.ob
        ob.aabb.center.x = self.x
        ob.aabb.center.y = self.y
        ob.aabb.hwidth = self.w / 2
        ob.aabb.hheight = self.h / 2

        if ob.node:
            ob.update_quadtree()

        # update snapshot
        self.entity.snapshots[self.position_snapshot] = clock()

        if self.parent != self._parent:
            self._parent = self.parent
            self.entity.snapshots[self.parent_snapshot] = clock()

    def on_destroy(self):
        self.entity.ob.remove()

    def initialize(self):
        # quadtree junk
        ob = self.entity.ob
        ob.aabb.center.x = self.x or random() - 0.5
        ob.aabb.center.y = self.y or random() - 0.5
        # self.entity.pos = ob.aabb.center
        self.entity.region.quadtree.insert(ob)
        self._parent = self.parent

        self.entity.snapshots[self.position_snapshot] = 0
        self.entity.snapshots[self.parent_snapshot] = 0

    def position_snapshot(self):
        return 'Bfffff', (
            packet_types.POSITION_UPDATE,
            self.x, self.y, self.r,
            self.vx, self.vy
        )

    def parent_snapshot(self):
        return 'BI', (
            packet_types.PARENT_UPDATE,
            self.get_parent_id()
        )

    def get_parent_id(self):
        if self.parent:
            return self.parent.id

        return 0

    def teleport(self, x, y=None):
        if y is None and isinstance(x, Vector2):
            self.x = x.x
            self.y = x.y
        else:
            self.x = x
            self.y = y

        self._update()

    def find_nearby(self, radius, exclude=None, flags=0, components=None):
        _q_aabb.center.update(self.entity.ob.aabb.center)
        _q_aabb.hwidth = _q_aabb.hheight = radius

        if exclude is None:
            exclude = set()

        if exclude is True:
            exclude = {self.entity}

        return self.entity.region.quadtree.query_aabb_ents(_q_aabb, exclude, flags, components)

    def get_pos(self, copy=False):
        if copy:
            return self.entity.ob.aabb.center.copy()

        return self.entity.ob.aabb.center


class Mass(BaseComponent):
    value = 1.1


class Volume(BaseComponent):
    value = 1.2
