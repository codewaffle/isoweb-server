from functools import partial
from time import time
from component import BaseComponent
from component.network import string_replicator, float_replicator


class Mesh(BaseComponent):
    data = {
        'model': 'models/quad.json',
        'scale': 1.0,
        'z': 0.01,
        'material': {
            'type': 'MeshLambertMaterial',
            'map': 'textures/dev.png',
        }
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[float_replicator(partial(getattr, data, 'scale'), 'scale')] = time()
        entity.snapshots[float_replicator(partial(getattr, data, 'z'), 'z')] = time()
        entity.snapshots[string_replicator(partial(getattr, data, 'model'), 'model')] = time()
        entity.snapshots[string_replicator(partial(data.material.get, 'map'), 'map')] = time()
