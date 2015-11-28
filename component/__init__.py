import glob
import os
import os.path
import sys
from inspect import isclass, getmembers
from component.base import BaseComponent
from util import AttributeDict
import logging
log = logging.getLogger(__name__)
# this is a silly place


modules = glob.glob(os.path.dirname(__file__) + '/*.py')

__all__ = list(
    set([os.path.basename(f)[:-3] for f in modules]) - {'__init__', 'base'}
)

from . import *


def component_filter(m):
    return m != BaseComponent and isclass(m) and issubclass(m, BaseComponent)


registry = AttributeDict()


def load_components():
    g = globals()
    for mod in __all__:
        for clsname, cls in getmembers(getattr(sys.modules[__name__], mod), component_filter):
            # ignore things imported into the module (TODO : find a better way)
            if not cls.__module__.endswith(mod):
                continue

            if clsname in registry:
                log.fatal('Duplicate Component: %s', clsname)
                raise RuntimeError('Duplicate Component', clsname, cls, mod)
            registry[clsname] = cls


load_components()


def get(classname):
    return registry[classname]
