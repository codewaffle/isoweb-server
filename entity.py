from math import atan2, pi
from struct import pack
from time import time
import ujson
import component
from component.base import BaseComponent
from isoweb_time import clock
from menu import Menu
import packet_types
from util import memoize, AttributeDict, time_to_clock, TrackedDictionary, TrackAttributes
import util


class ObFlags:
    REPLICATE = 1


class SnapshotContainer(dict):
    def __init__(self, ent):
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
        self.snapshots = None
        self.ob = EntityOb(self)
        self.dirty = False
        self.valid = True
        self.components = []
        self._component_names = set()
        self.modified = self.created = time()
        self.parent = None

        self.tracked_components = TrackedDictionary()

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

    def set_modified(self):
        self.modified = time()

    @property
    def modified_clock(self):
        return time_to_clock(self.modified)

    @property
    def name(self):
        if self._name is None:
            return self.entity_def.name

    def set_region(self, region):
        self.region = region
        self.snapshots = SnapshotContainer(self)
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
            yield x

    def initialize(self):
        for c in self.components:
            c.initialize()

    @property
    def scheduler(self):
        return self.region.scheduler

    def schedule(self, task):
        self.scheduler.schedule(func=task)

    def has_component(self, key):
        if isinstance(key, (str, bytes)):
            return key in self._component_names
        elif issubclass(key, BaseComponent):
            return key.__name__ in self._component_names

    def __contains__(self, item):
        return self.has_component(item)

    def add_component(self, comp_name, initialize=True, entdef=None, **data):
        comp_class = component.get(comp_name)
        if entdef is not None:
            comp = comp_class(self, entdef.component_data[comp_class])
        else:
            comp = comp_class(self)

        if getattr(comp, 'tracked_attributes', None):
            # store a reference to the component..
            self.tracked_components[comp_name] = comp
            # and then hook the component's tracker up to update the timestamp (but keep the reference)
            # dirty but fancy.. just the way I like it.
            comp._tracking._tracked_parent = (comp_name, self.tracked_components)

        object.__setattr__(self, comp_class.__name__, comp)
        self.components.append(comp)
        self._component_names.add(comp_name)
        [setattr(comp, k, v) for k, v in data.items()]

        if initialize:
            comp.initialize()

        return comp

    def add_components(self, components, initialize=True, entdef=None):
        if isinstance(components, (list, tuple, set)):
            for comp_name in components:
                self.add_component(comp_name, initialize=initialize, entdef=entdef)
        elif isinstance(components, dict):
            for comp_name, data in components.items():
                self.add_component(comp_name, initialize=initialize, entdef=entdef, **data)
        else:
            raise ValueError('Components is not valid')

    def update_components(self, components):
        """
        Update existing components and create new ones for missings.
        """
        kset = set(components.keys())
        to_update = self._component_names & set(components.keys())
        to_create = kset - to_update

        for comp_name in to_update:
            getattr(self, comp_name).__dict__.update(components[comp_name])

        to_init = [
            self.add_component(comp_name, initialize=False, **components[comp_name])
            for comp_name in to_create
        ]

        for comp_name in to_init:
            comp_name.initialize()

    def changes_after(self, ts):
        for ss_func, ss_time in self.snapshots.items():
            if ss_time >= ts:
                yield ss_func()

        if self.tracked_components.modified > ts:
            mods = {comp_name: comp.get_exports(ts) for comp_name, comp in self.tracked_components.get_modified_after(ts).items()}
            mods = {k: v for k, v in mods.items() if v}

            if mods:
                mods = ujson.dumps(mods, double_precision=3).encode('utf8')
                yield (
                    'BH%ds' % len(mods), (
                        packet_types.ENTITY_UPDATE,
                        len(mods),
                        mods
                    )
                )

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
        self.Position.r = atan2(look_dir.y, look_dir.x) + pi / 2.

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
        def _keep_always(comp_name):
            return comp_name not in self.entity_def.component_names

        def _filter_empty(items):
            return (i for i in items if i[1] or _keep_always(i[0]))

        return dict(
            _filter_empty((
                (comp.__class__.__name__, comp.modified_persists)
                for comp in self.components
            ))
        )

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

