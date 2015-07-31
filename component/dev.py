from functools import partial
from math import pi
from random import randint, uniform
from time import clock

from component import BaseComponent
from component.base import component_method, MenuComponent
from component.network import string_replicator
from mathx.vector2 import Vector2


class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 100)'
    }

    @component_method
    def initialize(self):
        self.entity.snapshots[string_replicator(partial(getattr, self.data, 'hit_area'), 'hit_area')] = clock()


class Choppable(MenuComponent):
    @component_method
    def get_menu(self, ent):
        return {
            '!chop': ('Chop with bare hands', self.chop)
        }

    @component_method
    def chop(self, chopper):
        chopper.controller.set_queue([
            chopper.controller.move_near_task(self.entity.pos, 3),
            (self.do_chop, (chopper,))
        ])

    @component_method
    def do_chop(self, chopper):
        self.entity.destroy()
        for x in range(randint(1, 3)):
            self.island.spawn('log', pos=self.pos + Vector2.random_inside(4.0), rot=uniform(0, pi * 2.0))


class Dragger(BaseComponent):
    @component_method
    def initialize(self):
        self.cache.update({
            'contribution': Vector2(),
            'draggable': None
        })

    @component_method
    def get_drag_force(self):
        return 5.0


class Draggable(MenuComponent):
    data = {
        'drag_handles': [
            Vector2(0.5, 0.0)  # attach to bottom center by default
        ]
    }

    @component_method
    def initialize(self):
        self.initialize_menu()
        self.cache['draggers'] = set()
        self.cache['scheduled'] = False

    @component_method
    def get_menu(self, ent):
        if ent in self.cache['draggers']:
            return {
                '!stop_dragging': ('Stop dragging', self.stop_drag)
            }

        return {
            '!drag': ('Start dragging', self.drag)
        }

    @component_method
    def drag(self, dragger):
        dragger.controller.set_queue([
            dragger.controller.move_near_task(self.drag_handle_near(dragger.pos), 2.0),
            (self.do_drag, (dragger,))
        ])

    @component_method
    def stop_drag(self, dragger):
        try:
            self.cache['draggers'].remove(dragger)
        except KeyError:
            pass

    @component_method
    def drag_handle_near(self, pos):
        return self.pos

    @component_method
    def do_drag(self, dragger):
        self.cache['draggers'].add(dragger)

        if not self.cache['scheduled']:
            self.start_schedule()

    @component_method
    def start_schedule(self):
        self.cache['scheduled'] = True
        self.schedule(self.update)

    @component_method
    def update(self, _):
        if not self.cache['draggers']:
            self.cache['scheduled'] = False
            return

        dt = 1/20.
        drag_force = Vector2()

        # reel in draggables and apply their drag force

        for d in self.cache['draggers']:
            diff = (d.pos - self.pos)
            dist = diff.magnitude
            dragdir = diff / dist

            if dist > 1.5:
                dist_diff = dist - 1.5
                d.Position.teleport(d.pos - dragdir * dist_diff * 0.5)
                drag_force.add(dragdir * dist_diff * d.Dragger.get_drag_force() * 0.5)

        self.entity.Position.teleport(self.pos + drag_force * dt)
        # TODO : uncomment this when rotation bugs are sorted out.
        # self.entity.look(drag_force)

        return -1 / 20.


class TileMap(BaseComponent):
    pass
