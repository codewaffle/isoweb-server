from functools import partial
from component.base import MenuComponent, component_method


class Container(MenuComponent):
    @component_method
    def get_menu(self, ent):
        return {
            '!view': ('View contents (noop)', self.view_contents)
        }

    @component_method
    def view_contents(self, ent):
        print ent, 'tried to view contents.'

    @component_method
    def store(self, target):
        assert 'Containable' in target.components

class Containable(MenuComponent):
    @component_method
    def get_menu(self, ent):
        # TODO : also include containers equipped by ent, and maybe containers dragged by ent.
        # do not compare to containers near ent at call because ent may be in range of containers that this is not
        # probably also do visibility check against world containers

        ret = {}

        # for now just find all containers near the containable
        for container in self.entity.find_nearby(5, components={'Container'}):
            ret['put_{}'.format(container.id)] = ('Put in {}'.format(container.name), partial(self.put_in, container))

        return ret

    @component_method
    def put_in(self, ent, container):
        self.entity.destroy()
        print 'putin on the ritz'
        pass