from time import time
from component import BaseComponent
from mathx import Vector2
from mathx import AABB
from random import random
from mathx.quadtree import NodeItem


class CharacterController(BaseComponent):
    pass


class EntityOb(NodeItem):
    def __init__(self, ent):
        NodeItem.__init__(self)
        self.ent = ent

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
        ob = entity.cache.ob
        ob.pos.x = data.x
        ob.pos.y = data.y
        ob.update_quadtree()

        # update snapshot
        entity.snapshots[entity.Position.snapshot] = time()

    @classmethod
    def initialize(cls, entity, data):
        # quadtree junk
        ob = entity.cache.ob = EntityOb(entity)
        ob.pos.x = data.x or random() - 0.5
        ob.pos.y = data.y or random() - 0.5
        entity.island.quadtree.insert(ob)

        entity.snapshots[entity.Position.snapshot] = 0

    @classmethod
    def snapshot(cls, entity, data):
        return 'ff', data.x, data.y

    @classmethod
    def teleport(cls, entity, data, x, y):
        data.x = x
        data.y = y
        cls._update(entity, data)

    @classmethod
    def find_nearby(cls, entity, data, radius, exclude=True):
        cls.q_aabb.center.update(entity.cache.ob.pos)
        cls.q_aabb.hwidth = cls.q_aabb.hheight = radius

        if exclude is True:
            exclude = {entity}

        return entity.island.quadtree.query_aabb_ents(cls.q_aabb, exclude)

    @classmethod
    def get_pos(cls, entity, data, copy=False):
        if copy:
            return entity.cache.ob.pos.copy()

        return entity.cache.ob.pos
