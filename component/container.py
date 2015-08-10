from collections import defaultdict
from functools import partial
from component.base import MenuComponent, component_method
from util import refreeze


class Container(MenuComponent):
    data = {
        'contents': {}
    }

    @component_method
    def initialize(self):
        self.initialize_menu()
        self.data.contents = {
            int(k): (
                (v[0][0], refreeze(v[0][1])), v[1]
            ) for k, v in self.data.contents.items()

        }
        self.data._registry = {v[0]: k for k,v in self.data.contents.items()}

        self.data._max = max(list(self.data.contents.keys()) + [0])

    @component_method
    def get_menu(self, ent):
        return {
            '!view': ('View contents (noop)', self.view_contents)
        }

    @component_method
    def view_contents(self, ent):
        print(ent, 'tried to view contents.')
        ent.controller.update_container(self.entity)
        ent.controller.show_container(self.entity)

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

        self.add_frozen(frozen)

        target.destroy()

    @component_method
    def add_frozen(self, frozen):
        try:
            idx = self.data._registry[frozen]
        except KeyError:
            idx = self.data._registry[frozen] = self.next_idx()
            self.data.contents[idx] = [frozen, 0]

        self.data.contents[idx][1] += 1

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
