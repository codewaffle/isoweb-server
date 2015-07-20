from functools import partial
from time import time
import packet_types
from util import memoize


class DataProxy(dict):
    def __init__(self, src):
        self.__dict__.update({
            '_src': src,
            # '_dirty': {}
        })

        super(DataProxy, self).__init__()

    def __missing__(self, key):
        return self._src[key]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        # self.__dict__['_dirty'][key] = time()
        dict.__setitem__(self, key, value)

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


def string_replicator(func, attr_name):
    name_len = len(attr_name)

    def inner():
        res = str(func())
        res_len = len(res)
        return 'HB{}sH{}s'.format(name_len, res_len), [packet_types.STRING_UPDATE, name_len, attr_name, res_len, res]

    return inner


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
