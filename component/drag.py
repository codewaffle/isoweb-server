from functools import partial
from component import BaseComponent
from component.base import MenuComponent
from mathx.vector2 import Vector2


class Dragger(BaseComponent):
    _cache = None

    def initialize(self):
        self._cache = {
            'contribution': Vector2(),
            'draggable': None
        }

    def get_drag_force(self):
        return 50.0


class Draggable(MenuComponent):
    _cache = None
    drag_handles = [
        Vector2(0.5, 0.0)  # attach to bottom center by default
    ]

    def initialize(self):
        self.initialize_menu()
        self._cache = {
            'draggers': set(),
            'scheduled': False
        }

    def get_menu(self, ent):
        if ent in self._cache['draggers']:
            return {
                '!stop_dragging': ('Stop dragging', partial(self.stop_drag, ent))
            }

        return {
            'drag': ('Start dragging', partial(self.drag, ent))
        }

    def drag(self, dragger):
        dragger.controller.set_queue([
            dragger.controller.move_near_task(self.drag_handle_near(dragger.pos), 0.5),
            (self.do_drag, (dragger,))
        ])

    def stop_drag(self, dragger):
        try:
            self._cache['draggers'].remove(dragger)
        except KeyError:
            pass

    def drag_handle_near(self, pos):
        return self.entity.pos

    def do_drag(self, dragger):
        self._cache['draggers'].add(dragger)

        if not self._cache['scheduled']:
            self.start_schedule()

    def start_schedule(self):
        self._cache['scheduled'] = True
        self.entity.schedule(self.update)

    def update(self):
        if not self._cache['draggers']:
            self._cache['scheduled'] = False
            return

        dt = 1 / 20.
        drag_force = Vector2()

        # reel in draggables and apply their drag force

        for d in self._cache['draggers']:
            diff = (d.pos - self.entity.pos)
            dist = diff.magnitude
            dragdir = diff / dist

            if dist > 0.5:
                dist_diff = dist - 0.5
                d.Position.teleport(d.pos - dragdir * dist_diff * 0.5)
                drag_force.add(dragdir * dist_diff * d.Dragger.get_drag_force() * 0.5)

        self.entity.Position.teleport(self.entity.pos + drag_force * dt)
        # TODO : uncomment this when rotation bugs are sorted out.
        # self.entity.look(drag_force)

        return -1 / 20.
