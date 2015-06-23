from uuid import uuid4
from logbook import Logger
from entity import Entity
from mathx import Vector2


class Player(Entity):
    socket = None
    move_target = None
    vel = 5

    def __init__(self):
        self.id = uuid4()
        super(Player, self).__init__()
        self.log = Logger('Player {}'.format(self.id))

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
                self.log.debug('{0} arrived at {1}', self, self.position)

    def move_to(self, x, y):
        self.move_target = Vector2(x, y)
        self.log.debug('move_to({0})', self.move_target)

    def __repr__(self):
        return '<Player({self.id})>'.format(self=self)