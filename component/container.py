from collections import defaultdict
from functools import partial
from component.base import MenuComponent
from util import refreeze


class Container(MenuComponent):
    data = {
        'contents': {}
    }

    def initialize(self):
        self.initialize_menu()
        self.data.contents = {
            int(k): (
                (v[0][0], refreeze(v[0][1])), v[1]
            ) for k, v in self.data.contents.items()

            }
        self.data._registry = {v[0]: k for k, v in self.data.contents.items()}

        self.data._max = max(list(self.data.contents.keys()) + [0])

    def get_menu(self, ent):
        return {
            '!view': ('View contents (noop)', partial(self.view_contents, ent))
        }

    def view_contents(self, ent):
        print(ent, 'tried to view contents.')
        ent.controller.update_container(self.entity)
        ent.controller.show_container(self.entity)

    def put(self, target):
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

            # we already have a dupe, destroy the original
            target.destroy()
            self.data.contents[idx][1] += 1
        except KeyError:
            # first entry in the container, keep it alive.
            idx = self.data._registry[frozen] = self.next_idx()
            self.data.contents[idx] = [frozen, 1]

        self.entity.set_dirty()

    def next_idx(self):
        self.data._max += 1
        return self.data._max


class Containable(MenuComponent):
    def get_menu(self, ent):
        # TODO : also include containers equipped by ent, and maybe containers dragged by ent.
        # do not compare to containers near ent at call because ent may be in range of containers that this is not
        # probably also do visibility check against world containers

        ret = {}

        # for now just find all containers near the containable
        for container in self.entity.find_nearby(5, components={'Container'}):
            ret['put_{}'.format(container.id)] = (
            'Put in {}'.format(container.name), partial(container.Container.put, self.entity))

        return ret
