from util import TrackAttributes


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
        track = dct.get('tracked_attributes', None)
        dct['exports'] = exports = set(dct.get('exports', set()))
        dct['persists'] = persists = set(dct.get('persists', set()))

        if track is None:
            track = exports | persists

        if track:
            parents = parents + (TrackAttributes,)
            dct['tracked_attributes'] = frozenset(track)

        obj = super().__new__(cls, name, parents, dct)

        return obj

INVALID_VALUE = object()


class BaseComponent(metaclass=BaseMeta):
    exports = []
    persists = []

    active = True
    init_order = 0

    def __init__(self, ent, entdef=None):
        self.name = self.__class__.__name__
        self.entity = ent
        self.entdef = entdef
        super(BaseComponent, self).__init__()

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

    def get_original_value(self, key):
        if self.entdef is not None:
            return self.entdef.get(key, getattr(self.__class__, key))

        return INVALID_VALUE

        #return getattr(self.__class__, key)

    @property
    def modified_persists(self):
        """
        return a dict of attributes listed in 'persists' that differ from the default...
        this is not as useful as I thought, as it will almost always differ from the class default
        but share values with the entitydef :(

        needs to
        """
        def _persists():
            return ((k, getattr(self, k)) for k in self.persists)

        return {k: v for k, v in _persists() if v != getattr(self.__class__, k)}

    def on_tracked_attribute_changed(self, key):
        if key in self.persists:
            self.entity.set_dirty()

        if key in self.exports:
            self.entity.set_modified()

    @classmethod
    def process_args(cls, args):
        """
        Classmethod to process data from yaml files and prepare it for use in the game.

        :param args:
        :return:
        """
        return args


class MenuComponent(BaseComponent):
    def initialize(self):
        self.initialize_menu()

    def initialize_menu(self):
        self.entity.menu_providers.add(self)

    def get_menu(self, ent):
        raise NotImplemented
