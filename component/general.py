from random import random
from time import time, clock
from component import BaseComponent
from mathx import AABB, Vector2, NodeItem
import packet_types


class EntityOb(NodeItem):
    def __init__(self, ent):
        NodeItem.__init__(self)
        self.ent = ent.reference

    def __repr__(self):
        return 'EntityOb({})'.format(repr(self.pos))


class Position(BaseComponent):
    data = {
        'x': 0.,
        'y': 0.,
        'r': 1.
    }

    q_aabb = AABB(Vector2(), 1)

    @classmethod
    def _update(cls, entity, data):
        # update quadtree position
        ob = entity.ob
        ob.pos.x = data.x
        ob.pos.y = data.y
        ob.update_quadtree()

        # update snapshot
        entity.snapshots[entity.Position.snapshot] = clock()

    @classmethod
    def initialize(cls, entity, data):
        # quadtree junk
        ob = entity.ob
        ob.pos.x = data.x or random() - 0.5
        ob.pos.y = data.y or random() - 0.5
        entity.pos = ob.pos
        entity.island.quadtree.insert(ob)

        entity.snapshots[entity.Position.snapshot] = 0

    @classmethod
    def snapshot(cls, entity, data):
        return 'Bfff', (packet_types.POSITION_UPDATE, data.x, data.y, data.r)

    @classmethod
    def teleport(cls, entity, data, x, y=None):
        if y is None and isinstance(x, Vector2):
            data.x = x.x
            data.y = x.y
        else:
            data.x = x
            data.y = y
        cls._update(entity, data)

    @classmethod
    def find_nearby(cls, entity, data, radius, exclude=True, flags=0):
        cls.q_aabb.center.update(entity.ob.pos)
        cls.q_aabb.hwidth = cls.q_aabb.hheight = radius

        if exclude is True:
            exclude = {entity}

        return entity.island.quadtree.query_aabb_ents(cls.q_aabb, exclude, flags)

    @classmethod
    def get_pos(cls, entity, data, copy=False):
        if copy:
            return entity.ob.pos.copy()

        return entity.ob.pos
