from math import atan2, pi
from component import BaseComponent


class CharacterController(BaseComponent):
    @classmethod
    def handle_menu_req_position(cls, entity, data, pos):
        pass

    @classmethod
    def handle_menu_req_entity(cls, entity, data, pos):
        pass

    @classmethod
    def handle_context_position(cls, entity, data, pos):
        raise NotImplemented

    @classmethod
    def handle_context_entity(cls, entity, data, pos):
        raise NotImplemented


class MeatbagController(CharacterController):
    data = {
        'move_speed': 2.0
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.controller = entity.MeatbagController
        entity.cache.moveTo = None

    @classmethod
    def handle_context_position(cls, entity, data, pos):
        # i don't know if this will ever be something other than 'move here'...
        # could use this for item actions (e.g. activate a shovel and then intercept context position to dig... dumb?)
        # but this will probably be handled by the client.. (activate shovel -> ask for target?).. don't know.
        if entity.cache.moveTo is None:
            entity.scheduler.schedule(func=entity.MeatbagController.update_move)
        entity.cache.moveTo = pos

    @classmethod
    def handle_context_entity(cls, entity, data, pos):
        pass

    @classmethod
    def update_move(cls, entity, data, dt):
        dt = 1/20.
        t = entity.cache.moveTo

        if t is None:
            return

        move_diff = t - entity.pos
        dist = move_diff.magnitude
        move_amt = data.move_speed * dt

        entity.Position.data.r = atan2(move_diff.y, move_diff.x) + pi / 2.

        if dist < move_amt:
            entity.Position.teleport(t)
            return
        else:
            entity.Position.teleport(entity.pos.lerp(t, move_amt / dist))

            return dt * -1.