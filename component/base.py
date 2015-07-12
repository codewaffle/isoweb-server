from functools import partial
from util import memoize


# TODO !!! entity defs should also be able to have properties that sit between themselves and entities..
# we may have a million entities that all have the same Sprite value but it might not be the
# default Sprite component value... also TODO : Sprite component.


class DataProxy(dict):
    def __init__(self, src):
        dict.__setattr__(self, '_src', src)
        super(DataProxy, self).__init__()

    def __missing__(self, key):
        return self._src[key]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value


class ComponentProxy(object):
    def __init__(self, cls, entity):
        self._memo_cache = {}
        self.cls = cls
        self.entity = entity
        cls.on_attached(entity, self.data)

    @property
    @memoize
    def data(self):
        try:
            return self.entity._component_data[self.cls.__name__]
        except KeyError:
            data = self.entity._component_data[self.cls.__name__] = DataProxy(
                self.entity.entity_def._component_data[self.cls.__name__]
            )
            return data

    @memoize
    def __getattr__(self, item):
        return partial(
            getattr(self.cls, item),
            self.entity,
            self.data
        )

    @memoize
    def __repr__(self):
        return '{}({})'.format(self.cls.__name__, self.entity)


class BaseComponent(object):
    _data = {}

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
