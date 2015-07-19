from time import time
from component import BaseComponent
from mathx import AABB, Vector2
from quadtree import NodeItem
from random import random

class CharacterController(BaseComponent):
    pass


class EntityOb(NodeItem):
    def __init__(self, ent):
        super(EntityOb, self).__init__()
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

        if exclude:
            return set(ob.ent for ob in entity.island.quadtree.query_aabb(cls.q_aabb)if ob.ent is not entity)
        else:
            return set(ob.ent for ob in entity.island.quadtree.query_aabb(cls.q_aabb))

    @classmethod
    def get_pos(cls, entity, data, copy=False):
        if copy:
            return entity.cache.ob.pos.copy()

        return entity.cache.ob.pos
