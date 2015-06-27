from uuid import uuid4
from logbook import Logger
from entity import Entity, EntityAttribute
from mathx import Vector2


class Player(Entity):
    sprite = EntityAttribute('sprites/player.png')

    def __init__(self):
        self.socket = None
        self.move_target = None
        self.vel = 5
        super(Player, self).__init__()

    def update(self, dt):
        if self.move_target:
            diff = self.move_target - self.position
            diff_mag = diff.magnitude

            if diff_mag > 0.1:
                move_dir = diff / diff_mag
                self.position += move_dir * min(diff_mag, self.vel*dt)
            else:
                self.position = self.move_target
                self.move_target = None
                self.log.debug('Arrived at {0}', self.position)

    def move_to(self, x, y):
        self.move_target = Vector2(x, y)
        self.log.debug('move_to({0})', self.move_target)
