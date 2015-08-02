from math import atan2, pi
import ujson
from menu import Menu
from util import memoize, AttributeDict


class EntityReference(object):
    """An invalidate-able reference to an Entity.

    When the Entity is disposed, .valid will be set false and the Entity can be
    returned to the pool after its memoize has been cleared.. and it will generate a new reference on demand.
    """
    def __init__(self, entity):
        self.__dict__.update({
            'entity': entity,
            'id': entity.id,
            'valid': True
        })

    def __getattr__(self, item):
        return getattr(self.entity, item)

    def __setattr__(self, key, value):
        raise RuntimeError("NO WAY JEEZE STOP IT")

    def __repr__(self):
        try:
            return 'EntityReference({})'.format(self.id)
        except AttributeError:
            return 'EntityReference(None)'

class ObFlags:
    REPLICATE = 1


class SnapshotContainer(dict):
    def __init__(self, ent, dirty_set):
        super(SnapshotContainer, self).__init__()
        self._ent = ent
        self._dirty_set = dirty_set

    def __setitem__(self, key, value):
        super(SnapshotContainer, self).__setitem__(key, value)
        self._dirty_set.add(self._ent)


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

    @property
    def name(self):
        if self._name is None:
            return self.entity_def.name

    def set_island(self, island):
        self.island = island
        self.snapshots = SnapshotContainer(self, island.dirty_set)
        island.entities_by_id[self.id] = self.reference
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
        return key in self.components

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

    @property
    @memoize
    def reference(self):
        return EntityReference(self)

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
        # reset Reference
        self.reference.__dict__.update({
            'entity': None,
            'valid': False
        })
        self.ob.flags = 0
        from component.general import EntityOb
        self.ob = EntityOb(self)
        del self._memo_cache
        self._memo_cache = {}

    def look(self, look_dir):
        self.Position.data.r = atan2(look_dir.y, look_dir.x) + pi / 2.

    def freeze(self):
        # loop over components, packaging them into frozensets
        # then, pack those into another frozenset
        # then, destroy this entity and return that frozenset.

        # the frozenset-of-sets entities should be usable as dictionary keys (and also serializable to disk!)
        pass

    @property
    def persistent_data(self):
        def public(cd):
            return {k: v for k,v in cd.items() if not k.startswith('_')}

        def persistable(cd):
            return {k: v for k, v in cd.items() if v or k not in self.entity_def.components}

        return persistable({k: public(v) for k, v in self.component_data.items()})

    def save_data(self, cur):
        try:
            data = {
                'id': self.id,
                'entitydef': self.entity_def.key,
                'ob_flags': self.ob.flags,
                'components': self.persistent_data
            }
            cur.put('ent-{}'.format(self.id), ujson.dumps(data, double_precision=3))
        except Exception as E:
            print 'wtf'
            raise
