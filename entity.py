from collections import defaultdict
from entitydef import definition_from_key
from util import memoize, AttributeDict
import component

class EntityReference(object):
    """An invalidate-able reference to an Entity.

    When the Entity is disposed, .valid will be set false and the Entity can be
    returned to the pool after its memoize has been cleared.. and it will generate a new reference on demand.
    """
    def __init__(self, entity):
        self.entity = entity
        self.valid = True


class Entity(object):
    """
    an Entity is a bag of component data that points to an EntityDef.
    """
    _frozen = False

    def __init__(self, entity_def):
        self._memo_cache = {}
        self._component_data = {}
        self.entity_def = entity_def
        self.island = None

    @classmethod
    def spawn(cls, entdef, components=None):
        if isinstance(entdef, basestring):
            entdef = definition_from_key(entdef)

        ent = cls(entdef)

        if isinstance(components, list):
            for comp_class in components:
                setattr(ent, comp_class.__name__, comp_class.bind(ent, False))
        elif isinstance(components, dict):
            for comp_class, data in components.items():
                comp = comp_class.bind(ent, False)
                setattr(ent, comp_class.__name__, comp)
                comp.data.update(data)

        ent._frozen = True
        return ent

    @memoize
    def __getattr__(self, item):
        # return memoized component proxy
        return getattr(self.entity_def, item).bind(self)

    def __setattr__(self, key, value):
        # this is mostly to prevent accidental ent.blah instead of ent.data.blah and might be modified/removed.
        assert not self._frozen
        object.__setattr__(self, key, value)

    def has_component(self, key):
        return hasattr(self.entity_def, key)

    @memoize
    def reference(self):
        return EntityReference(self)

    @property
    def data(self):
        return self._component_data
