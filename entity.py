from util import memoize, AttributeDict


class EntityReference(object):
    """An invalidate-able reference to an Entity.

    When the Entity is disposed, .valid will be set false and the Entity can be
    returned to the pool after its memoize has been cleared.. and it will generate a new reference on demand.
    """
    def __init__(self, entity):
        self.__dict__.update({
            'entity': entity,
            'valid': True
        })

    def __getattr__(self, item):
        return getattr(self.entity, item)

    def __setattr__(self, key, value):
        raise RuntimeError("NO WAY JEEZE STOP IT")

class ObFlags:
    REPLICATE = 1


class Entity(object):
    """
    an Entity is a bag of component data that points to an EntityDef.
    """

    _frozen = False
    _controller = None

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
        self.component_data = {}
        self.snapshots = {}
        self.pos = None  # replaced by whatever component handles position.
        self.ob = EntityOb(self)

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
