from random import random
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
