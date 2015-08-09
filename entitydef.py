import os
import fnmatch
from component.base import DataProxy
import component


class EntityDef:
    def __init__(self, data, key):
        self.key = key
        self.name = key.replace('_', ' ')
        self.component_data = {}
        self.components = set()

        if isinstance(data, dict):
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
            comp_name = c.pop('class')
            comp_class = component.get(comp_name)
            setattr(self, comp_name, comp_class)
            self.components.add(comp_name)

            dataproxy = self.component_data[comp_name] = DataProxy(comp_class.data)
            dataproxy.update(c)

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
                    _defs[def_key] = EntityDef(data, def_key)

def definition_from_key(def_key):
    return _defs[def_key]
