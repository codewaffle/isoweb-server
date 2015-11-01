from isoweb_time import clock
from component import BaseComponent
from mathx.vector2 import Vector2
import packet_types
from phys.space import PhysicsSpace
from phys.core import TestMember, RaftTestMember


class Position(BaseComponent):
    x = 0.
    y = 0.
    vx = 0.
    vy = 0.

    w = 1.
    h = 1.

    r = 0.  # rotation

    member = None

    _parent = None

    persists = ['x', 'y', 'vx', 'vy', 'w', 'h', 'r']

    def _update(self):
        if self.entity.space_member:
            self.x, self.y, self.r = self.entity.space_member.get_position_components()
            self.vx, self.vy = self.entity.space_member.get_velocity_components()

        # update snapshot
        self.entity.snapshots[self.position_snapshot] = clock()

        if self.entity.parent != self._parent:
            self._parent = self.entity.parent
            self.entity.snapshots[self.parent_snapshot] = clock()

    def __repr__(self):
        return '<Position {},{}>'.format(self.x, self.y)

    def on_destroy(self):
        self.entity.ob.remove()

    def initialize(self):
        self._parent = self.entity.parent

        assert self.entity.space_member, ':('
        self.entity.space_member.set_position_components(self.x, self.y)
        self.entity.space_member.set_velocity_components(self.vx, self.vy)

        self.entity.snapshots[self.position_snapshot] = 0
        self.entity.snapshots[self.parent_snapshot] = 0

    def position_snapshot(self):
        return 'Bfffff', (
            packet_types.POSITION_UPDATE,
            self.x, self.y, self.r,
            self.vx, self.vy
        )

    def parent_snapshot(self):
        return 'BI', (
            packet_types.PARENT_UPDATE,
            self.get_parent_id()
        )

    def get_parent_id(self):
        if self.entity.parent:
            return self.entity.parent.id

        return 0

    def teleport(self, x, y=None):
        if y is None and isinstance(x, Vector2):
            y = x.y
            x = x.x

        if self.entity.space_member:
            self.entity.space_member.set_position_components(x, y)
        else:
            self.x, self.y = x, y

        self._update()

    def find_nearby(self, radius, exclude=None, mask=0, components=None):
        ret = self.entity.space_member.find_nearby(radius, mask)

        if exclude is True:
            ret.difference_update({self.entity})
        elif exclude:
            ret.difference_update(exclude)

        return ret

    def get_pos(self):
        return Vector2(self.x, self.y)


class Space(BaseComponent):
    space = None
    boundary = None

    def initialize(self):
        self.space = self.entity.space = PhysicsSpace()
        self.entity.scheduler.schedule(func=self.simulate)

    def simulate(self):
        self.space.step(1/20.0)
        return -1/20.0


class TestPhysics(BaseComponent):
    def initialize(self):
        TestMember(self.entity)


class RaftPhysics(BaseComponent):
    def initialize(self):
        RaftTestMember(self.entity)