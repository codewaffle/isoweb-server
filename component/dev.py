from functools import partial
from math import atan2, pi, sin, cos
from random import random
from time import time, clock
from component import BaseComponent
from component.network import string_replicator
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

class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 50)'
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[string_replicator(partial(getattr, data, 'hit_area'), 'hit_area')] = clock()

class SimpleWander(BaseComponent):
    data = {
        'velocity': 1.0,
        'target': None
    }

    @classmethod
    def initialize(cls, entity, data):
        data.velocity = 2. + random() * 2.
        entity.scheduler.schedule(at=clock() + 2.0, func=entity.SimpleWander.update)

    @classmethod
    def update(cls, entity, data, dt):
        dt = 1/20.

        if data.target is None:
            data.target = Vector2(-64 + random() * 128., -64 + random() * 128.)

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
        entity.Position.data.r = atan2(move.y, move.x) + pi/2.
        return -1 / 20.


class Spiraler(BaseComponent):
    data = {
        'velocity': 1.0,
    }

    @classmethod
    def initialize(cls, entity, data):
        data.velocity = 2. + random() * 2.
        entity.scheduler.schedule(at=clock() + 2.0, func=entity.Spiraler.update)
        data.clock = 0

    @classmethod
    def update(cls, entity, data, dt):
        dt = 1/20.
        data.clock += dt

        entity.Position.teleport(
            sin(data.clock) * data.clock,
            cos(data.clock) * data.clock
        )

        return -1 / 20.
