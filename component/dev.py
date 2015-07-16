import struct
from time import time
from component import BaseComponent
import quadtree


class CharacterController(BaseComponent):
    pass


class EntityOb(quadtree.ob):
    def __init__(self, ent):
        self.ent = ent


class Position(BaseComponent):
    data = {
        'x': 1,
        'y': 2,
        'r': 1
    }

    @classmethod
    def _update(cls, entity, data):
        ob = entity.cache.ob
        entity.island.quadtree.delete(ob)
        ob.set_rect(data.x - data.r, data.y + data.r, data.x + data.r, data.y - data.r)
        entity.island.quadtree.insert(ob)
        entity.snapshots[entity.Position.snapshot] = time()

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[entity.Position.snapshot] = 0
        ob = entity.cache.ob = EntityOb(entity)
        ob.set_rect(data.x - data.r, data.y + data.r, data.x + data.r, data.y - data.r)

        entity.island.quadtree.insert(entity.cache.ob)

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
        pass