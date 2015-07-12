from functools import partial
from util import memoize


class ComponentProxy(object):
    def __init__(self, cls, entity):
        self._memo_cache = {}
        self.cls = cls
        self.entity = entity
        cls.on_attached(entity, self.data)

    @property
    def data(self):
        return self.entity._component_data[self.cls.__name__]

    @memoize
    def __getattr__(self, item):
        return partial(getattr(self.cls, item), self.entity, self.data)

    @memoize
    def __repr__(self):
        return '{}({})'.format(self.cls.__name__, self.entity)


class BaseComponent(object):
    @classmethod
    def on_attached(cls, entity, data):
        pass

    @classmethod
    def yield_actions(cls, entity, data, actor, target):
        if False:
            yield  # this is on purpose! do not remove.

    @classmethod
    # not memoized - memoize on accessor! classmethods never ever garbage collect.
    def proxy(cls, entity):
        return ComponentProxy(cls, entity)
