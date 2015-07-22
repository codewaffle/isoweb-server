from math import atan2, pi
from random import random
from time import time
from component import BaseComponent
from mathx import Vector2


class CharacterController(BaseComponent):
    pass



class Crawler(BaseComponent):
    @classmethod
    def initialize(cls, entity, data):
        entity.cache.crawler_vel = Vector2(-2.5 + random() * 5., -2.5 + random() * 5.)

        entity.scheduler.schedule(func=entity.Crawler.update)

    @classmethod
    def update(cls, entity, data, dt):
        entity.Position.teleport(entity.ob.pos.x + entity.cache.crawler_vel.x * dt, entity.ob.pos.y + entity.cache.crawler_vel.y * dt)
        entity.cache.crawler_vel -= (entity.ob.pos * dt * 0.1)
        return 1/30.

class SimpleWander(BaseComponent):
    data = {
        'velocity': 1.0,
        'target': None
    }

    @classmethod
    def initialize(cls, entity, data):
        data.velocity = 5. + random() * 5.
        entity.scheduler.schedule(at=time() + 2.0, func=entity.SimpleWander.update)

    @classmethod
    def update(cls, entity, data, dt):
        if data.target is None:
            data.target = Vector2(-256 + random() * 512., -256 + random() * 512.)

        diff = data.target - entity.ob.pos
        mag = diff.magnitude

        if mag == 0:
            entity.ob.pos.update(data.target.x, data.target.y)
            data.target = None
            return

        norm = diff / mag

        move = norm * min(dt * data.velocity, mag)

        if dt * data.velocity > mag:
            data.target = None

        entity.Position.teleport(entity.ob.pos.x + move.x,
                                 entity.ob.pos.y + move.y)
        entity.Position.data.r = atan2(move.y, move.x) - pi/2.
        return -1 / 20.
