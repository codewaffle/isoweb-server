from collections import defaultdict
from functools import partial
from component.base import MenuComponent, component_method


class Container(MenuComponent):
    data = {
        'contents': {}
    }

    @component_method
    def initialize(self):
        self.initialize_menu()
        self.data.contents = {}
        self.data._registry = {}
        self.data._max = 0

    @component_method
    def get_menu(self, ent):
        return {
            '!view': ('View contents (noop)', self.view_contents)
        }

    @component_method
    def view_contents(self, ent):
        print ent, 'tried to view contents.'

    @component_method
    def put(self, target, putter=None):
        try:
            target.Position.destroy()
        except AttributeError:
            pass

        try:
            target.Replicated.destroy()
        except AttributeError:
            pass

        frozen = target.freeze()

        try:
            idx = self.data._registry[frozen]
        except KeyError:
            idx = self.data._registry[frozen] = self.next_idx()
            self.data.contents[idx] = ['type', frozen, 0]

        self.data.contents[idx][2] += 1

        target.destroy()
        self.entity.set_dirty()

    @component_method
    def next_idx(self):
        self.data._max += 1
        return self.data._max

class Containable(MenuComponent):
    @component_method
    def get_menu(self, ent):
        # TODO : also include containers equipped by ent, and maybe containers dragged by ent.
        # do not compare to containers near ent at call because ent may be in range of containers that this is not
        # probably also do visibility check against world containers

        ret = {}

        # for now just find all containers near the containable
        for container in self.entity.find_nearby(5, components={'Container'}):
            ret['put_{}'.format(container.id)] = ('Put in {}'.format(container.name), partial(container.Container.put, self.entity))

        return ret
