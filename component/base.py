from util import track_attributes


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


class BaseMeta(type):
    def __new__(cls, name, parents, dct):
        obj = super().__new__(cls, name, parents, dct)

        track = dct.get('exports', [])
        track.extend(dct.get('persists', []))

        if track:
            return track_attributes(*track)(obj)

        return obj


class BaseComponent(metaclass=BaseMeta):
    exports = []
    persists = []

    active = True

    def __init__(self, ent):
        self.entity = ent

    def initialize(self):
        pass

    def deactivate(self):
        if self.active:
            self.active = False
            self.on_deactivate()

    def activate(self):
        if not self.active:
            self.active = True
            self.on_activate()

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def destroy(self):
        self.on_destroy()
        try:
            self.entity.components.remove(self)
            delattr(self.entity, self.__class__.__name__)
        except KeyError:
            pass

    def on_destroy(self):
        pass

    @property
    def modified_persists(self):
        def _persists():
            return ((k, getattr(self, k)) for k in self.persists)

        return {k: v for k, v in _persists() if v != getattr(self.__class__, k)}

    def on_tracked_attribute_changed(self, key):
        if key in self.persists:
            self.entity.set_dirty()
        else:
            self.entity.set_modified()

    def get_tracked_attributes(self, after=-1):
        pass  # replaced by metaclass


class MenuComponent(BaseComponent):
    def initialize(self):
        self.initialize_menu()

    def initialize_menu(self):
        self.entity.menu_providers.add(self)

    def get_menu(self, ent):
        raise NotImplemented
