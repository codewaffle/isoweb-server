from math import atan2, pi
import struct
from isoweb_time import clock
from component import BaseComponent
import entitydef
from menu import MultipleDefaultMenuItems
import packet_types
from util import to_bytes


class ControllerComponent(BaseComponent):
    _socket = None
    _queue = None

    def controller_initialize(self):
        self._queue = []

    def initialize(self):
        self.controller_initialize()

    def handle_menu_req_position(self, pos):
        pass

    def handle_menu_req_entity(self, ent):
        menu = ent.get_menu(self.entity)

        if not menu:
            return

        # send menu
        fmt = ['>BfIB']
        data = [packet_types.CMD_MENU_REQ_ENTITY, clock(), ent.id, len(menu)]

        for kw, (desc, func) in menu:
            fmt.append('B{}sB{}s'.format(len(kw), len(desc)))
            data.extend([len(kw), kw, len(desc), desc])

        self._socket.send(struct.pack(''.join(fmt), *to_bytes(data)))

    def handle_menu_exec_entity(self, ent, action):
        menu = ent.get_menu(self.entity)
        menu.execute(action)

    def handle_context_position(self, pos):
        raise NotImplemented

    def handle_context_entity(self, ent):
        ctx_menu = ent.get_context_menu(self.entity)

        if not ctx_menu:
            return

        try:
            ctx_menu.execute_default()
        except MultipleDefaultMenuItems:
            # send the truncated menu
            fmt = ['>BfIB']
            data = [packet_types.CMD_MENU_REQ_ENTITY, clock(), ent.id, len(ctx_menu)]

            for kw, (desc, func) in ctx_menu:
                fmt.append('B{}sB{}s'.format(len(kw), len(desc)))
                data.extend([len(kw), kw, len(desc), desc])

            self._socket.send(struct.pack(''.join(fmt), *to_bytes(data)))
            return

    def update_container(self, container):

        fmt = ['>BfIH']
        dat = [packet_types.CONTAINER_UPDATE, clock(), container.id, len(container.Container.contents)]

        for idx, c in container.Container.contents.items():
            entdef = entitydef.definition_from_key(c[0][0])
            fmt.append('HIffB{}sB{}s'.format(len(entdef.name), len(entdef.component_data['Sprite'].sprite)))

            dat.extend([
                idx,
                c[1],
                1,
                1,
                len(entdef.name),
                entdef.name,
                len(entdef.component_data['Sprite'].sprite),
                entdef.component_data['Sprite'].sprite
            ])

        packed = struct.pack(''.join(fmt), *to_bytes(dat))
        self._socket.send(packed)

    def show_container(self, container):
        self._socket.send(struct.pack('>BfI', packet_types.CONTAINER_SHOW, clock(), container.id))

    def hide_container(self, container):
        self._socket.send(struct.pack('>BfI', packet_types.CONTAINER_HIDE, clock(), container.id))

    def handle_hide_container(self, container):
        print('player requested that we hide container:', container)

    def update_queue(self):
        q = self._queue
        try:
            func, args = q[0]
        except IndexError:
            return

        ret = func(*args)

        if ret is None:  # return None = move to next task
            q.pop(0)
            if len(q) > 0:
                return -1 / 20.
        elif ret is False:  # False = abort queue
            del self._queue[:]
        else:
            return ret

    def set_queue(self, new_queue):
        if new_queue and not self._queue:
            self.entity.schedule(self.update_queue)

        self._queue = new_queue

    def queue_task(self, task, args):
        if not self._queue:
            self.entity.schedule(self.update_queue)

        self._queue.append((task, args))


class MeatbagController(ControllerComponent):
    move_speed = 3.0

    def initialize(self):
        self.entity.controller = self.entity.MeatbagController
        self.controller_initialize()

    def handle_context_position(self, pos):
        # i don't know if this will ever be something other than 'move here'...
        # could use this for item actions (e.g. activate a shovel and then intercept context position to dig... dumb?)
        # but this will probably be handled by the client.. (activate shovel -> ask for target?).. don't know.

        self.set_queue([
            (self.do_move_to, (pos,))
        ])

    def move_near_task(self, pos, dist=0.5):
        near_pos = pos + (self.entity.pos - pos).normalized * dist
        return self.do_move_to, (near_pos,)

    def do_move_to(self, dest):
        dt = 1 / 10.

        if dest is None:
            print('ff')
            return False

        if not self.entity.region_member:
            return dt * -1


        move_diff = dest - self.entity.pos
        dist = move_diff.magnitude
        move_dir = move_diff / dist

        curVel = self.entity.region_member.velocity
        desiredVel = move_dir * min(dist, 3.0)
        velDiff = desiredVel - curVel

        velDist = velDiff.magnitude
        velNorm = velDiff/velDist

        move_diff = velNorm * 20 #min(dist, 5)

        self.entity.region_member.set_force(move_diff.x, move_diff.y)
        self.entity.region_member.set_angle(atan2(curVel.y, curVel.x) + pi/2)

        return dt * -1

        # TODO : FIX THESE TERRIBLE HAX

        move_amt = self.move_speed * dt

        self.entity.Position.r = atan2(move_diff.y, move_diff.x) + pi/2

        if dist < move_amt:
            self.entity.Position.teleport(dest)
            self.entity.Position.vx = self.entity.Position.vy = 0
            self.entity.region.log.debug('{} arrived at {}', self.entity, dest)

            return None
        else:
            self.entity.Position.teleport(self.entity.pos.lerp(dest, move_amt / dist))
            self.entity.Position.vx = move_diff.x / dist * self.move_speed
            self.entity.Position.vy = move_diff.y / dist * self.move_speed

            return dt * -1.
