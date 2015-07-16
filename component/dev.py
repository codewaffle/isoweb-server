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
    def _update_quadtree(cls, entity, data):
        ob = entity.cache.ob
        entity.island.quadtree.delete(ob)
        ob.set_rect(data.x - data.r, data.y + data.r, data.x + data.r, data.y - data.r)
        entity.island.quadtree.insert(ob)

    @classmethod
    def initialize(cls, entity, data):
        ob = entity.cache.ob = EntityOb(entity)
        ob.set_rect(data.x - data.r, data.y + data.r, data.x + data.r, data.y - data.r)

        entity.island.quadtree.insert(entity.cache.ob)

    @classmethod
    def teleport(cls, entity, data, x, y):
        data.x = x
        data.y = y
        cls._update_quadtree(entity, data)

    @classmethod
    def find_nearby(cls, entity, data, radius, exclude=True):
        pass