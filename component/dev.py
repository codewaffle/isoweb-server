from functools import partial
from time import clock

from component import BaseComponent
from component.network import string_replicator


class Interactive(BaseComponent):
    data = {
        'hit_area': 'Circle(0, 0, 50)'
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[string_replicator(partial(getattr, data, 'hit_area'), 'hit_area')] = clock()


