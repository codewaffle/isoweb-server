from math import atan2, pi
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


class Entity(object):
    """
    an Entity is a bag of component data that points to an EntityDef.
    """

    _frozen = False
    _controller = None
    _menu_providers = None

    def __init__(self, entity_def):
        from component.general import EntityOb

        self._memo_cache = {}  # for @memoize
        self.cache = AttributeDict()
        self.entity_def = entity_def
        self.island = None
        self.island_id = 0  # TODO : this will eventually be tied to the island that spawned this entity..
        # TODO cont: i think 4 billion entities generated per island should be enough. we can spawn subentities somehow if needed.
        self.id = id(self)  # this will be generated in a better manner as well..

        # this is a name/DataProxy dict.
        self._menu_providers = set()
        self.component_data = {}
        self.snapshots = {}
        self.pos = None  # replaced by whatever component handles position.
        self.ob = EntityOb(self)

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

    def do_menu(self, user, action):
        if not self._menu_providers:
            return False

        for mp in self.menu_providers:
            menu = mp.get_menu(user)

            data = menu.get(action, None)

            if data:
                data[1](user)

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
