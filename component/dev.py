from functools import partial
from time import clock

from component import BaseComponent
from component.base import component_method, MenuComponent
from component.network import string_replicator


class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 50)'
    }

    @component_method
    def initialize(self):
        self.entity.snapshots[string_replicator(partial(getattr, self.data, 'hit_area'), 'hit_area')] = clock()


class Choppable(MenuComponent):
    @component_method
    def get_menu(self, ent):
        return {
            '!chop': self.chop
        }

    @component_method
    def chop(self, chopper):
        print "HELP I AM BEING CHOPPED BY", chopper
