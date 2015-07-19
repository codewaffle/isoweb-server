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


class Entity(object):
    """
    an Entity is a bag of component data that points to an EntityDef.
    """
    _frozen = False

    def __init__(self, entity_def):
        self._memo_cache = {}  # for @memoize
        self.cache = AttributeDict()
        self.entity_def = entity_def
        self.island = None

        # this is a name/DataProxy dict.
        self.component_data = {}
        self.snapshots = {}

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

    def __setattr__(self, key, value):
        # this is mostly to prevent accidental ent.blah instead of ent.data.blah and might be modified/removed.
        assert not self._frozen
        object.__setattr__(self, key, value)

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
        for ss_func, ss_time in self.snapshots.iteritems():
            if ss_time > ts:
                yield ss_func()