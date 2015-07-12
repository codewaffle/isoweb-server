from collections import defaultdict
from util import memoize, AttributeDict


class Entity(object):
    def __init__(self, entity_def):
        self._memo_cache = {}
        self._component_data = {}
        self.entity_def = entity_def

    @memoize
    def __getattr__(self, item):
        # return memoized component proxy
        return getattr(self.entity_def, item).proxy(self)

