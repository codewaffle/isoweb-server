from collections import defaultdict
from util import memoize, AttributeDict
import component

class EntityReference(object):
    """An invalidate-able reference to an Entity.

    When the Entity is disposed, .valid will be set false and the Entity can be
    returned to the pool after its memoize has been cleared.. and it will generate a new reference on demand.
    """
    def __init__(self, entity):
        self.entity = entity
        self.valid = True


class Entity(object):
    """
    an Entity is a bag of component data that points to an EntityDef.
    """
    _frozen = False

    def __init__(self, entity_def):
        self._memo_cache = {}
        self._component_data = {}
        self.entity_def = entity_def
        self.Transform = component.registry.Transform.bind(self, False)
        self._frozen = True

    @memoize
    def __getattr__(self, item):
        # return memoized component proxy
        return getattr(self.entity_def, item).bind(self)

    def __setattr__(self, key, value):
        # this is mostly to prevent accidental ent.blah instead of ent.data.blah and might be modified/removed.
        assert not self._frozen
        object.__setattr__(self, key, value)

    def has_component(self, key):
        return hasattr(self.entity_def, key)

    @memoize
    def reference(self):
        return EntityReference(self)

    @property
    def data(self):
        return self._component_data
