import glob
import os
import os.path
import sys
from inspect import isclass, getmembers
from component.base import BaseComponent

modules = glob.glob(os.path.dirname(__file__) + '/*.py')

__all__ = list(
    set([os.path.basename(f)[:-3] for f in modules]) - {'__init__', 'base'}
)

from . import *

def component_filter(m):
    return m != BaseComponent and isclass(m) and issubclass(m, BaseComponent)

_components = {}
def load_components():
    for mod in __all__:
        for clsname, cls in getmembers(getattr(sys.modules[__name__], mod), component_filter):
            _components[clsname] = cls


load_components()

def component_by_name(classname):
    return _components[classname]


