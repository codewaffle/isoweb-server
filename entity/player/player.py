from uuid import uuid4
from entity import Entity


class Player(Entity):
    socket = None
    move_target = None
    vel = 5

    def __init__(self):
        self.id = uuid4()
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
