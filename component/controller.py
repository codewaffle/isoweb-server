from math import atan2, pi
import struct
from isoweb_time import clock
from component import BaseComponent
import entitydef
from mathx.vector2 import Vector2
from menu import MultipleDefaultMenuItems
import packet_types
from util import to_bytes


class Controller(BaseComponent):
    def initialize(self):
        pass

    def dummy(self, packet):
        print("DUMMY!")


class SimpleMovementController(Controller):
    def initialize(self):
        self.entity.packet_handlers[packet_types.CMD_CONTEXTUAL_POSITION] = self.move_to

    def move_to(self, packet):
        x, y = struct.unpack_from('>ff', packet, 1)

        assert isinstance(self.entity.controller, MeatbagController)
        self.entity.controller.set_queue([
            (self.entity.controller.do_move_to, (Vector2(x,y),))
        ])


class MenuController(Controller):
    def initialize(self):
        self.entity.packet_handlers[packet_types.CMD_MENU_REQ_ENTITY] = self.dummy
        self.entity.packet_handlers[packet_types.CMD_CONTEXTUAL_ENTITY] = self.dummy
        self.entity.packet_handlers[packet_types.CMD_MENU_EXEC_ENTITY] = self.dummy

        self.entity.packet_handlers[packet_types.CMD_MENU_REQ_POSITION] = self.dummy
        self.entity.packet_handlers[packet_types.CMD_MENU_EXEC_POSITION] = self.dummy


class ContainerController(Controller):
    def initialize(self):
        self.entity.packet_handlers[packet_types.CONTAINER_HIDE] = self.dummy
        self.entity.packet_handlers[packet_types.CONTAINER_SHOW] = self.dummy
        self.entity.packet_handlers[packet_types.CONTAINER_INDEX_MENU_REQ] = self.dummy
        self.entity.packet_handlers[packet_types.CONTAINER_UPDATE] = self.dummy


class CraftingController(Controller):
    def initialize(self):
        self.entity.packet_handlers[packet_types.CRAFTING_SHOW] = self.dummy
        self.entity.packet_handlers[packet_types.CRAFTING_HIDE] = self.dummy
        self.entity.packet_handlers[packet_types.CRAFTING_INDEX] = self.dummy
        self.entity.packet_handlers[packet_types.CRAFTING_DETAIL] = self.dummy
        self.entity.packet_handlers[packet_types.CRAFTING_EXECUTE] = self.dummy


class ChatController(Controller):
    _socket = None
    _chatters = set()

    def initialize(self):
        self.entity.packet_handlers[packet_types.MESSAGE] = self.chat
        self._chatters.add(self)

    def chat(self, payload):
        message_len, = struct.unpack_from('>H', payload, 1)
        message, = struct.unpack_from('>{}s'.format(message_len), payload, 3)
        #broadcast(self.entity.name, message)
        self.entity_text(self.entity, message)

    def entity_text(self, ent, message):
        print('[EntityText] {}: {}'.format(ent, message))
        pkt = struct.pack(
                '>BfBIH{}s'.format(len(message)),
                *to_bytes([packet_types.MESSAGE, clock(), 3, ent.id, len(message), message])
        )

        for ch in self._chatters:
            ch.send(pkt)

    def send(self, packet):
        self._socket.send(packet)

    @classmethod
    def broadcast(cls, message_from, message):
        print('[Broadcast] {}: {}'.format(message_from, message))
        pkt = struct.pack(
                '>BfBB{}sH{}s'.format(len(message_from), len(message)),
                *to_bytes([packet_types.MESSAGE, clock(), 1, len(message_from), message_from, len(message), message])
        )

        for ch in cls._chatters:
            ch.send(pkt)


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

    def move_near_task(self, pos, dist=0.5):
        near_pos = pos + (self.entity.pos - pos).normalized * dist
        return self.do_move_to, (near_pos,)

    def do_move_to(self, dest):
        dt = 1 / 20.

        if dest is None:
            print('ff')
            return False

        if not self.entity.space_member:
            return dt * -1

        move_diff = dest - self.entity.pos
        dist = move_diff.magnitude
        move_dir = move_diff / dist
        curVel = self.entity.space_member.velocity

        if dist < 0.05:  # we're here
            self.entity.space_member.set_force(0, 0)
            self.entity.space_member.set_velocity(0, 0)
            self.entity.Position._update()
            return None
        if dist < 3.0:  # arrive
            desiredVel = move_dir * 4.0 * (dist / 3.0)
        else:
            desiredVel = move_dir * 4.0

        velDiff = desiredVel - curVel

        velDist = velDiff.magnitude
        velNorm = velDiff/velDist

        force = velDiff * 5.0 * self.entity.space_member.get_mass()

        self.entity.space_member.set_angle(atan2(move_dir.y, move_dir.x) - pi/2)
        self.entity.space_member.set_force(force.x, force.y)

        return dt * -1
