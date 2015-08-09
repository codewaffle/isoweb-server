from math import atan2, pi
import ujson
from component.base import BaseComponent
from menu import Menu
from util import memoize, AttributeDict
import util


class ObFlags:
    REPLICATE = 1


class SnapshotContainer(dict):
    def __init__(self, ent, dirty_set):
        super(SnapshotContainer, self).__init__()
        self._ent = ent

    def __setitem__(self, key, value):
        super(SnapshotContainer, self).__setitem__(key, value)
        self._ent.set_dirty()


def next_id():
    pass


class Entity(object):
    """
    an Entity is a bag of component data that points to an EntityDef.
    """
    _name = None
    _frozen = False
    _controller = None
    _menu_providers = None

    def __init__(self, ent_id):
        from component.general import EntityOb

        self._memo_cache = {}  # for @memoize
        self.cache = AttributeDict()
        self.island = None
        self.island_id = 0  # TODO : this will eventually be tied to the island that spawned this entity..
        self.id = ent_id
        self.entity_def = None
        self._menu_providers = set()
        self.component_data = {}
        self.snapshots = None
        self.pos = None  # replaced by whatever component handles position.
        self.ob = EntityOb(self)
        self.dirty = False

    def set_dirty(self):
        if not self.dirty:
            self.dirty = True
            self.island.dirty_set.add(self)

    def set_clean(self, remove=False):
        self.dirty = False

        if remove:
            self.island.dirty_set.remove(self)

    @property
    def name(self):
        if self._name is None:
            return self.entity_def.name

    def set_island(self, island):
        self.island = island
        self.snapshots = SnapshotContainer(self, island.dirty_set)
        island.entities_by_id[self.id] = self
        island.entities.add(self)

    @property
    def menu_providers(self):
        if self._menu_providers is None:
            self._menu_providers = set()

        return self._menu_providers

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, val):
        if val is None and self._controller is not None:
            del self._controller
        else:
            self._controller = val

    @property
    def components(self):
        return self.entity_def.components | set(self.component_data.keys())

    def initialize(self):
        for c in self.components:
            getattr(self, c).initialize()

    @property
    def scheduler(self):
        return self.island.scheduler

    @memoize
    def __getattr__(self, item):
        # return memoized component proxy
        return getattr(self.entity_def, item).bind(self)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def schedule(self, task):
        self.scheduler.schedule(func=task)

    def has_component(self, key):
        if isinstance(key, basestring):
            return key in self.components
        elif issubclass(key, BaseComponent):
            return key.__name__ in self.components

    def __contains__(self, item):
        return self.has_component(item)

    def add_component(self, comp_class, initialize=True, **data):
        comp = comp_class.bind(self, False)
        object.__setattr__(self, comp_class.__name__, comp)
        comp.data.update(data)

        if initialize:
            comp.initialize()

        return comp

    def add_components(self, components, initialize=True):
        if isinstance(components, (list, tuple)):
            for comp_class in components:
                self.add_component(comp_class, initialize=initialize)
        elif isinstance(components, dict):
            for comp_class, data in components.items():
                self.add_component(comp_class, initialize=initialize, **data)
        else:
            raise ValueError('Components is not valid')

    def update_components(self, components):
        """
        Update existing components and create new ones for missings.
        """
        from component import c

        kset = set(components.keys())
        to_update = self.components & set(components.keys())
        to_create = kset - to_update

        for comp in to_update:
            getattr(self, comp).data.update(components[comp])

        to_init = [self.add_component(getattr(c, comp), initialize=False, **components[comp]) for comp in to_create]

        for comp in to_init:
            comp.initialize()

    def changes_after(self, ts):
        ret = []
        for ss_func, ss_time in self.snapshots.iteritems():
            if ss_time >= ts:
                ret.append(ss_func())

        return ret

    def get_menu(self, user):
        # users use menus, I guess..
        menu = Menu()

        if self._menu_providers is None:
            return {}

        for mp in self.menu_providers:
            menu.update(mp.get_menu(user))

        return menu

    def get_context_menu(self, user):
        max_i = -1
        menu = None

        for a, mi in self.get_menu(user):
            if a.startswith('!'):
                i = 1
                while a[i] == '!':
                    i += 1

                if i < max_i:
                    continue
                elif i == max_i:
                    menu[a] = mi
                if i > max_i:
                    max_i = i
                    menu = {a: mi}

        if menu:
            return Menu.from_dict(menu)
        else:
            return None

    def destroy(self):
        self.island.destroy_entity(self)

    def look(self, look_dir):
        self.Position.data.r = atan2(look_dir.y, look_dir.x) + pi / 2.

    def freeze(self):
        result = self.entity_def.name, util.freeze_dict(self.persistent_data)
        return result

    def find_nearby(self, radius, exclude=True, flags=0, components=None):
        return self.Position.find_nearby(radius, exclude, flags, components)

    @property
    def persistent_data(self):
        def public(cd):
            return {k: v for k,v in cd.items() if not k.startswith('_')}

        def persistable(cd):
            return {k: v for k, v in cd.items() if v or k not in self.entity_def.components}

        return persistable({k: public(v) for k, v in self.component_data.items() if k not in ('NetworkViewer', )})

    @property
    def db_key(self):
        return 'ent-{}'.format(self.id)

    def save_data(self, cur):
        try:
            data = {
                'id': self.id,
                'entitydef': self.entity_def.key,
                'ob_flags': self.ob.flags,
                'components': self.persistent_data
            }
            cur.put(self.db_key, ujson.dumps(data, double_precision=3))
        except Exception as E:
            print 'wtf'
            raise

        self.dirty = False

