from collections import defaultdict
from util import memoize, AttributeDict

class EntityReference(object):
    """An invalidate-able reference to an Entity.

    When the Entity is disposed, .valid will be set false and the Entity can be
    returned to the pool after its memoize has been cleared.. and it will generate a new reference on demand.
    """
    def __init__(self, entity):
        self.entity = entity
        self.valid = True


class Entity(object):
    def __init__(self, entity_def):
        self._memo_cache = {}
        self._component_data = {}
        self.entity_def = entity_def

    @memoize
    def __getattr__(self, item):
        # return memoized component proxy
        return getattr(self.entity_def, item).proxy(self)

    @memoize
    def reference(self):
        return EntityReference(self)