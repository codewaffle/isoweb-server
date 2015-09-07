from functools import partial, wraps

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
        # self.__dict__['_dirty'][key] = clock()
        dict.__setitem__(self, key, value)


class ComponentProxy:
    def __init__(self, cls, entity, bind_def):
        self._memo_cache = {}
        self.cls = cls
        self.entity = entity
        self.bind_def = bind_def

    @property
    def region(self):
        return self.entity.region

    @property
    def pos(self):
        return self.entity.pos

    @property
    @memoize  # the object that is returned is memoized, not any of the data inside
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

    @property
    def exports(self):
        assert self.entity and self.entity.entity_def
        base = self.def_exports

        return {
            k: self.data[k]
            for k in self.cls.exports
            if self.data[k] != base[k]
        }

    @property
    def def_exports(self):
        return {
            k: self.entity.entity_def.component_data[self.cls.__name__][k]
            for k in self.cls.exports
        }

    @memoize
    def __getattr__(self, item):
        return partial(
            getattr(self.cls, item),
            self
        )

    @memoize
    def __repr__(self):
        return '{}({})'.format(self.cls.__name__, self.entity)

    def schedule(self, task):
        return self.entity.schedule(task)

current_component_class = None


def component_method(f):
    @wraps(f)
    def wrapper(cls, *a, **kw):
        global current_component_class
        current_component_class = cls
        return f(*a, **kw)

    return classmethod(wrapper)


class BaseComponent:
    data = {
        'active': True
    }

    exports = []

    def __init__(self):
        raise RuntimeError("class-only")

    @component_method
    def initialize(self):
        pass

    @component_method
    def deactivate(self):
        if self.data.active:
            self.data.active = False
            self.on_deactivate()

    @component_method
    def activate(self):
        if not self.data.active:
            self.data.active = True
            self.on_activate()

    @component_method
    def on_activate(self):
        pass

    @component_method
    def on_deactivate(self):
        pass

    @component_method
    def destroy(self):
        self.on_destroy()
        try:
            del self.entity.component_data[current_component_class.__name__]
        except KeyError:
            pass

    @component_method
    def on_destroy(self):
        pass

    # these are mostly to shut up pycharm/idea
    entity = NotImplemented
    region = NotImplemented
    pos = NotImplemented
    cache = NotImplemented

    def schedule(self, task):
        raise NotImplemented

    @classmethod
    # not memoized - memoize on accessor! classmethods never ever garbage collect.
    def bind(cls, entity, bind_def=True):
        return ComponentProxy(cls, entity, bind_def)


class MenuComponent(BaseComponent):
    @component_method
    def initialize(self):
        self.initialize_menu()

    @component_method
    def initialize_menu(self):
        self.entity.menu_providers.add(self)

    @component_method
    def get_menu(self, ent):
        raise NotImplemented