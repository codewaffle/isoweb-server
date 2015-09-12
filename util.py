import collections
from functools import partial
from time import time

from isoweb_time import clock
from twisted.internet import task, reactor

_class_cache = {}


def load_class(classpath):
    mod, cls = classpath.rsplit('.', 1)
    val = getattr(__import__(mod), cls)
    _class_cache[classpath] = val

    return val


def get_class(classpath):
    return _class_cache.get(classpath, load_class(classpath))


class OrderedDefaultdict(collections.OrderedDict):
    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwargs)

    def __missing__ (self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self):  # optional, for pickle support
        args = (self.default_factory,) if self.default_factory else ()
        return self.__class__, args, None, None, self.items()

def memodict(f):
    """ (FAST) Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


class memoize:
    """cache the return value of a method

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.

    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:
    class Obj:
        @memoize
        def add_to(self, arg):
            return self + arg
    Obj.add_to(1) # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)

    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj._memo_cache
        except AttributeError:
            cache = obj._memo_cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res


class AttributeDict(dict):
    def __getattribute__(self, item):
        return dict.get(self, item)

    def __setattr__(self, key, value):
        self[key] = value


def freeze_dict(d):
    def _filter(val):
        if isinstance(val, dict):
            return freeze_dict(val)
        return val

    return frozenset(((k, _filter(v)) for k, v in d.items()))


def refreeze(obj):
    def _filter(x):
        if isinstance(x, (list, tuple, set)):
            return refreeze(x)
        return x

    return frozenset(_filter(x) for x in obj)


def noop():
    pass


def sleep(seconds, callback=noop):
    return task.deferLater(reactor, seconds, callback)


def to_bytes(data):
    if isinstance(data, list):
        return [x.encode('utf8') if isinstance(x, str) else x for x in data]
    elif isinstance(data, str):
        return data.encode('utf8')
    else:
        return data


class TrackedDictionary(dict):
    """
    Tracks a timestamp for every item.

    Provides method `get_modified_after(timestamp)` to return a sub-dictionary
    containing only values that have changed after `timestamp`.
    """
    _tracked_parent = None
    DELETED = object()
    INVALID = object()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tracking = {k: -1 for k in self.keys()}
        self.modified = clock()

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            # we are borg
            value = TrackedDictionary(value)

        if isinstance(value, TrackedDictionary) and (not value._tracked_parent or value._tracked_parent[1] != self):
            value._tracked_parent = (key, self)

        if value != self.get(key, TrackedDictionary.INVALID):
            self.touch(key)
            super().__setitem__(key, value)

    def __delitem__(self, key):
        self.touch(key)
        super().__delitem__(key)

    def touch(self, key):
        self._tracking[key] = self.modified = clock()
        try:
            _k, _p = self._tracked_parent
            _p.touch(_k)
        except (TypeError, ):
            pass

    def get_modified_after(self, when):
        return {k: self.get(k, TrackedDictionary.DELETED) for k, d in self._tracking.items() if d > when}


class TrackAttributes:
    tracked_attributes = frozenset()
    on_tracked_attribute_changed = None

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_tracking', TrackedDictionary())
        [self.__setattr__(k, getattr(self, k)) for k in self.tracked_attributes]
        super().__init__()

    def __setattr__(self, key, value):
        changed = value != getattr(self, key, TrackedDictionary.INVALID)
        super().__setattr__(key, value)

        if key in self.tracked_attributes:
            if value == getattr(self.__class__, key):
                # delete and save memory!
                try:
                    del self._tracking[key]
                except KeyError:
                    return
            else:
                self._tracking[key] = value

        if changed and self.on_tracked_attribute_changed:
            self.on_tracked_attribute_changed(key)

    def get_tracked_attributes(self, after=-1):
        if after == -1:
            return {k: getattr(self, k) for k in self.tracked_attributes}

        def filter_deleted(k, v):
            return k, v if v != TrackedDictionary.DELETED else getattr(self, k)

        return dict(
            (filter_deleted(k, v)
             for k, v in self._tracking.get_modified_after(after).items())
        )


clock_time_start = time() - clock()


def clock_to_time(clock_value):
    return clock_time_start + clock_value


def time_to_clock(time_value):
    return time_value - clock_time_start
