import os
import fnmatch
import xxhash
import ujson
from component.base import DataProxy
import component
from logbook import Logger
from util import memoize
import logging
log = logging.getLogger(__name__)
xx = xxhash.xxh64()


class EntityDef:
    """
    EntityDefs serve as templates for new Entities.
    """
    by_digest = {}
    by_key = {}

    @classmethod
    def get_hash(cls, key):
        xx.reset()
        xx.update(key)
        return xx.intdigest()

    def __init__(self, key, data):
        self.key = key
        self.log = Logger('EntityDef({})'.format(repr(self.key)))

        self.digest = self.get_hash(key)

        assert self.key not in EntityDef.by_key
        EntityDef.by_key[key] = self

        assert self.digest not in EntityDef.by_digest
        EntityDef.by_digest[self.digest] = self

        self.name = key.replace('_', ' ')
        self.component_data = {}
        self.component_names = set()
        self.component_classes = set()

        if isinstance(data, list):
            self.load_components(data)
        elif isinstance(data, dict):
            self.load_data(data)
        else:
            raise RuntimeError

    def load_data(self, data):
        for k, v in data.items():
            if k == 'components':
                self.load_components(v)
            else:
                print(k, '=', v)
                setattr(self, k, v)

    def load_components(self, data):
        for c in data:
            if isinstance(c, dict):
                try:
                    comp_name = c.pop('component')
                    comp_args = c.copy()
                except KeyError:
                    # look for short-form component (Mass: 10) - must only be one entry!
                    assert len(c) == 1, repr(c)
                    comp_name, comp_args = list(c.items())[0]

                    if comp_name == 'meta': # wat dis
                        self.__dict__.update(comp_args)

                    if not isinstance(comp_args, dict):
                        comp_args = {'value': comp_args}
            elif isinstance(c, str):
                comp_name = c
                comp_args = {}
            else:
                raise NotImplemented

            try:
                comp_class = component.get(comp_name)
            except KeyError:
                self.log.warn("Component '{}' does not exist", comp_name)
                continue
                # raise ValueError("Component '{}' does not exist".format(comp_name))

            setattr(self, comp_name, comp_class)
            self.component_names.add(comp_name)
            self.component_classes.add(comp_class)
            self.component_data[comp_class] = comp_class.process_args(comp_args)

    @property
    @memoize  # EntityDefs are static after load so we can cache this
    def exports(self):
        return dict(e for e in {
            comp.__name__: {k: self.component_data[comp].get(k, getattr(comp, k))
                            for k in comp.exports}
            for comp in self.component_classes
        }.items() if e[1])

    @property
    @memoize
    def exports_json(self):
        return ujson.dumps(self.exports, double_precision=3).encode('utf8')

_defs = {}


def load_defs():
    import yaml

    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    def load(yaml_file):
        with open(yaml_file, 'r') as fp:
            return yaml.load(fp, Loader=Loader)

    for root, dirs, files in os.walk('defs/entity'):
        for fn in files:
            if fnmatch.fnmatch(fn, '*.yml'):
                print(fn)
                for def_key, data in load(os.path.join(root, fn)).items():
                    if def_key in _defs:
                        log.fatal('Duplicate def_key: %s', def_key)
                        raise RuntimeError('Duplicate def_key', def_key, fn)
                    _defs[def_key] = EntityDef(def_key, data)


def definition_from_key(def_key):
    return _defs[def_key]
