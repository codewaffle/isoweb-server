from math import atan2, pi
import struct
from time import clock
from component import BaseComponent
from component.base import component_method
import packet_types


class ControllerComponent(BaseComponent):
    data = {
        'socket': None
    }

    @component_method
    def controller_initialize(self):
        self.data.queue = []

    @component_method
    def initialize(self):
        self.controller_initialize()

    @component_method
    def handle_menu_req_position(self, pos):
        pass

    @component_method
    def handle_menu_req_entity(self, ent):
        menu = ent.get_menu(self.entityref)

        if not menu:
            return

        # send menu
        fmt = ['>BfIB']
        data = [packet_types.CMD_MENU_REQ_ENTITY, clock(), ent.id, len(menu)]

        for kw, (desc, func) in menu.items():
            fmt.append('B{}sB{}s'.format(len(kw), len(desc)))
            data.extend([len(kw), kw, len(desc), desc])

        self.data.socket.send(struct.pack(''.join(fmt), *data))

    @component_method
    def handle_menu_exec_entity(self, ent, action):
        menu = ent.get_menu(self.entityref)
        func = menu.get(action, None)

        if func:
            func(self.entityref)

    @component_method
    def handle_context_position(self, pos):
        raise NotImplemented

    @component_method
    def handle_context_entity(self, ent):
        ctx_menu = ent.get_context_menu(self.entityref)

        if not ctx_menu:
            return

        if len(ctx_menu) > 1:
            # send the truncated menu
            fmt = ['>BfIB']
            data = [packet_types.CMD_MENU_REQ_ENTITY, clock(), ent.id, len(ctx_menu)]

            for kw, (desc, func) in ctx_menu.items():
                fmt.append('B{}sB{}s'.format(len(kw), len(desc)))
                data.extend([len(kw), kw, len(desc), desc])

            self.data.socket.send(struct.pack(''.join(fmt), *data))
            return
        else:
            # one thing to do? do it.
            ctx_menu.values()[0][1](self.entityref)

    @component_method
    def update_queue(self, dt):
        q = self.data.queue
        try:
            func, args = q[0]
        except IndexError:
            return

        ret = func(*args)

        if ret is None:  # return None = move to next task
            q.pop(0)
            if len(q) > 0:
                return -1/20.
        elif ret is False:  # False = abort queue
            del self.data.queue[:]
        else:
            return ret

    @component_method
    def set_queue(self, new_queue):
        if new_queue and not self.data.queue:
            self.entity.schedule(self.update_queue)

        self.data.queue = new_queue

    @component_method
    def queue_task(self, task, args):
        if not self.data.queue:
            self.entity.schedule(self.update_queue)

        self.data.queue.append((task, args))


class MeatbagController(ControllerComponent):
    data = {
        'move_speed': 3.0
    }

    @component_method
    def initialize(self):
        self.entity.controller = self.entity.MeatbagController
        self.controller_initialize()

    @component_method
    def handle_context_position(self, pos):
        # i don't know if this will ever be something other than 'move here'...
        # could use this for item actions (e.g. activate a shovel and then intercept context position to dig... dumb?)
        # but this will probably be handled by the client.. (activate shovel -> ask for target?).. don't know.

        self.set_queue([
            (self.do_move_to, (pos, ))
        ])

    @component_method
    def move_near_task(self, pos, dist=1):
        near_pos = pos + (self.entity.pos - pos).normalized * dist
        return self.do_move_to, (near_pos, )

    @component_method
    def do_move_to(self, pos):
        dt = 1/20.
        t = pos

        if t is None:
            print 'ff'
            return False

        move_diff = t - self.entity.pos
        dist = move_diff.magnitude
        move_amt = self.data.move_speed * dt

        self.entity.Position.data.r = atan2(move_diff.y, move_diff.x) + pi / 2.

        if dist < move_amt:
            self.entity.Position.teleport(t)
            print 'done'

            return None
        else:
            self.entity.Position.teleport(self.entity.pos.lerp(t, move_amt / dist))

            return dt * -1.
