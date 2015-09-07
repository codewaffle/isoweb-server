from math import atan2, pi
import ujson
import component
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


class Entity:
    """
    an Entity is a bag of component data that points to an EntityDef.
    """
    _registry = {}
    _name = None
    _controller = None
    _menu_providers = None

    def __init__(self, ent_id):
        from component.physical import EntityOb
        self._registry[ent_id] = self

        self._memo_cache = {}  # for @memoize
        self.cache = AttributeDict()
        self.region = None
        self.region_id = 0
        self.id = ent_id
        self.entity_def = None
        self._menu_providers = set()
        self.component_data = {}
        self.snapshots = None
        self.ob = EntityOb(self)
        self.dirty = False
        self.valid = True
        self.components = []

    @classmethod
    def get(cls, ent_id):
        return cls._registry[ent_id]

    def set_dirty(self):
        if not self.dirty:
            self.dirty = True
            self.region.dirty_set.add(self)

    def set_clean(self, remove=False):
        self.dirty = False

        if remove:
            self.region.dirty_set.remove(self)

    @property
    def name(self):
        if self._name is None:
            return self.entity_def.name

    def set_region(self, region):
        self.region = region
        self.snapshots = SnapshotContainer(self, region.dirty_set)
        region.entities.add(self)

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

    def component_iter(self):
        for x in self.components:
            yield getattr(self, x)

    def initialize(self):
        for c in self.components:
            c.initialize()

    @property
    def scheduler(self):
        return self.region.scheduler

    @memoize
    def __getattr__(self, item):
        # return memoized component proxy
        return getattr(self.entity_def, item).bind(self)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def schedule(self, task):
        self.scheduler.schedule(func=task)

    def has_component(self, key):
        if isinstance(key, (str, bytes)):
            return key in self.components
        elif issubclass(key, BaseComponent):
            return key.__name__ in self.components

    def __contains__(self, item):
        return self.has_component(item)

    def add_component(self, comp_name, initialize=True, **data):
        comp_class = component.get(comp_name)
        comp = comp_class(self)
        object.__setattr__(self, comp_class.__name__, comp)
        comp.data.update(data)

        if initialize:
            comp.initialize()

        self.components.append(comp)

        return comp

    def add_components(self, components, initialize=True):
        if isinstance(components, (list, tuple, set)):
            for comp_name in components:
                self.add_component(comp_name, initialize=initialize)
        elif isinstance(components, dict):
            for comp_name, data in components.items():
                self.add_component(comp_name, initialize=initialize, **data)
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
        for ss_func, ss_time in self.snapshots.items():
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
            if a.startswith(b'!'):
                i = 1
                while a[i] == b'!':
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
        self.region.destroy_entity(self)

    def look(self, look_dir):
        self.Position.data.r = atan2(look_dir.y, look_dir.x) + pi / 2.

    def freeze(self):
        result = self.entity_def.name, util.freeze_dict(self.persistent_data)
        return result

    def find_nearby(self, radius, exclude=True, flags=0, components=None):
        return self.Position.find_nearby(radius, exclude, flags, components)

    @property
    def pos(self):
        return self.Position.get_pos()

    @pos.setter
    def pos(self, value):
        self.Position.teleport(value)

    @property
    def persistent_data(self):
        def transform(cd):
            if isinstance(cd, dict):
                return {k: transform(v) for k,v in cd.items()}
            elif isinstance(cd, Entity):
                return cd.id
            else:
                return cd

        def public(cd):
            return {k: transform(v) for k, v in cd.items() if not k.startswith('_')}

        def persistable(cd):
            return {k: v for k, v in cd.items() if v or k not in self.entity_def.components}

        return persistable({k: public(v) for k, v in self.component_data.items() if k not in ('NetworkViewer', )})

    def get_db_key(self):
        return 'ent-{}'.format(self.id).encode('utf8')

    def save_data(self, cur):
        try:
            data = {
                'id': self.id,
                'entitydef': self.entity_def.key,
                'ob_flags': self.ob.flags,
                'components': self.persistent_data
            }
            cur.put(self.get_db_key(), ujson.dumps(data, double_precision=3).encode('utf8'))
        except Exception as E:
            print('wtf')
            raise

        self.dirty = False

