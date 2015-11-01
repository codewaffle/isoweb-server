from isoweb_time import clock

cdef class TrackedDictionary(dict):
    """
    Tracks a timestamp for every item.

    Provides method `get_modified_after(timestamp)` to return a sub-dictionary
    containing only values that have changed after `timestamp`.
    """
    DELETED = object()
    INVALID = object()

    cdef object _tracking
    cdef float modified
    cdef object _tracked_parent

    def __cinit__(self):
        self._tracked_parent = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tracking = {k: -1 for k in self.keys()}
        self.modified = clock()

    def set_parent(self, val):
        self._tracked_parent = val

    cpdef bint modified_after(self, ts):
        return self.modified > ts

    def __setitem__(self, key, value):
        if isinstance(value, TrackedDictionary) and (not value._tracked_parent or value._tracked_parent[1] != self):
            value._tracked_parent = (key, self)
        elif isinstance(value, dict):
            # we are borg
            value = TrackedDictionary(value)
            value._tracked_parent = (key, self)

        if value != self.get(key, TrackedDictionary.INVALID):
            self.touch(key)
            super().__setitem__(key, value)

    def __delitem__(self, key):
        self.touch(key)
        super().__delitem__(key)

    def erase(self, key):
        """
        delete a key completely, including tracking information
        """
        super().__delitem__(key)
        del self._tracking[key]

    cpdef touch(self, key):
        cdef TrackedDictionary _p
        self._tracking[key] = self.modified = clock()

        try:
            _k, _p = self._tracked_parent
            _p.touch(_k)
        except (TypeError, ):
            pass

    def get_modified_after(self, when):
        def _unpack(v):
            return v.get_modified_after(when) if isinstance(v, TrackedDictionary) else v

        return {k: _unpack(self.get(k, TrackedDictionary.DELETED)) for k, d in self._tracking.items() if d > when}