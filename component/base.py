from functools import partial
from util import memoize


class DataProxy(dict):
    def __init__(self, src):
        self.__dict__.update({
            '_src': src,
            '_dirty': False
        })

        super(DataProxy, self).__init__()

    def __missing__(self, key):
        return self._src[key]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self.__dict__['dirty'] = True
        self[key] = value


class ComponentProxy(object):
    def __init__(self, cls, entity, bind_def):
        self._memo_cache = {}
        self.cls = cls
        self.entity = entity
        self.bind_def = bind_def

    @property
    @memoize
    def data(self):
        try:
            return self.entity.component_data[self.cls.__name__]
        except KeyError:
            if self.bind_def:
                data = self.entity.component_data[self.cls.__name__] = DataProxy(
                    self.entity.entity_def.component_data[self.cls.__name__]
                )
            else:
                data = self.entity.component_data[self.cls.__name__] = DataProxy(
                    self.cls.data
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
    data = {}

    @classmethod
    def initialize(cls, entity, data):
        pass

    @classmethod
    def yield_actions(cls, entity, data, actor, target):
        if False:
            yield  # this is on purpose! do not remove.

    @classmethod
    # not memoized - memoize on accessor! classmethods never ever garbage collect.
    def bind(cls, entity, bind_def=True):
        return ComponentProxy(cls, entity, bind_def)

