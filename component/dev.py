from functools import partial
from time import clock

from component import BaseComponent
from component.base import component_method
from component.network import string_replicator


class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 50)'
    }

    @component_method
    def initialize(self):
        self.entity.snapshots[string_replicator(partial(getattr, self.data, 'hit_area'), 'hit_area')] = clock()


