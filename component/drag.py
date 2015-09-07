from functools import partial
from component import BaseComponent
from component.base import component_method, MenuComponent
from mathx.vector2 import Vector2


class Dragger(BaseComponent):
    @component_method
    def initialize(self):
        self.data._cache = {
            'contribution': Vector2(),
            'draggable': None
        }

    @component_method
    def get_drag_force(self):
        return 50.0


class Draggable(MenuComponent):
    data = {
        'drag_handles': [
            Vector2(0.5, 0.0)  # attach to bottom center by default
        ]
    }

    @component_method
    def initialize(self):
        self.initialize_menu()
        self.data._cache = {
            'draggers': set(),
            'scheduled': False
        }

    @component_method
    def get_menu(self, ent):
        if ent in self.data._cache['draggers']:
            return {
                '!stop_dragging': ('Stop dragging', partial(self.stop_drag, ent))
            }

        return {
            'drag': ('Start dragging', partial(self.drag, ent))
        }

    @component_method
    def drag(self, dragger):
        dragger.controller.set_queue([
            dragger.controller.move_near_task(self.drag_handle_near(dragger.pos), 0.5),
            (self.do_drag, (dragger,))
        ])

    @component_method
    def stop_drag(self, dragger):
        try:
            self.data._cache['draggers'].remove(dragger)
        except KeyError:
            pass

    @component_method
    def drag_handle_near(self, pos):
        return self.entity.pos

    @component_method
    def do_drag(self, dragger):
        self.data._cache['draggers'].add(dragger)

        if not self.data._cache['scheduled']:
            self.start_schedule()

    @component_method
    def start_schedule(self):
        self.data._cache['scheduled'] = True
        self.entity.schedule(self.update)

    @component_method
    def update(self):
        if not self.data._cache['draggers']:
            self.data._cache['scheduled'] = False
            return

        dt = 1/20.
        drag_force = Vector2()

        # reel in draggables and apply their drag force

        for d in self.data._cache['draggers']:
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