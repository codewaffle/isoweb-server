import os
import fnmatch
import xxhash
import ujson
from component.base import DataProxy
import component
from util import memoize

xx = xxhash.xxh64()

class EntityDef:
    """
    EntityDefs serve as templates for new Entities.
    """
    by_digest = {}
    by_key = {}

    def __init__(self, key, data):
        self.key = key

        xx.reset()
        xx.update(key)
        self.digest = xx.intdigest()

        assert self.key not in EntityDef.by_key
        EntityDef.by_key[key] = self

        assert self.digest not in EntityDef.by_digest
        EntityDef.by_digest[self.digest] = self

        self.name = key.replace('_', ' ')
        self.component_data = {}
        self.components = set()

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
            comp_name = c.pop('component')
            comp_class = component.get(comp_name)
            setattr(self, comp_name, comp_class)
            self.components.add(comp_name)

            dataproxy = self.component_data[comp_name] = DataProxy(comp_class.data)
            dataproxy.update(c)

    @property
    @memoize
    def exports(self):
        return dict(e for e in {
            comp: {k: self.component_data[comp][k] for k in getattr(self, comp).exports}
            for comp in self.components
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
                for def_key, data in load(os.path.join(root, fn)).items():
                    _defs[def_key] = EntityDef(def_key, data)

def definition_from_key(def_key):
    return _defs[def_key]
