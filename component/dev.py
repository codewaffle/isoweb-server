from time import time
from component import BaseComponent
from quadtree import NodeItem


class CharacterController(BaseComponent):
    pass


class EntityOb(NodeItem):
    def __init__(self, ent):
        super(EntityOb, self).__init__()
        self.ent = ent


class Position(BaseComponent):
    data = {
        'x': 1,
        'y': 2,
        'r': 1
    }

    @classmethod
    def _update(cls, entity, data):
        # update quadtree position
        ob = entity.cache.ob
        ob.x = data.x
        ob.y = data.y
        ob.update_quadtree()

        # update snapshot
        entity.snapshots[entity.Position.snapshot] = time()

    @classmethod
    def initialize(cls, entity, data):
        # quadtree junk
        ob = entity.cache.ob = EntityOb(entity)
        ob.x = data.x
        ob.y = data.y
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
        pass