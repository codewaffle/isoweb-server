from functools import partial
from time import clock

from component import BaseComponent
from component.base import component_method, MenuComponent
from component.network import string_replicator


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
        print "HELP I AM BEING CHOPPED BY", chopper
        chopper.controller.set_queue([
            chopper.controller.move_near_task(self.entity.pos, 3),
            (self.do_chop, (chopper, ))
        ])

    @component_method
    def do_chop(self, chopper):
        print "CHOP CHOP CHOP", chopper
