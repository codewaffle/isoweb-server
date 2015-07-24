from functools import partial
from time import time, clock
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
        entity.snapshots[float_replicator(partial(getattr, data, 'scale'), 'scale')] = clock()
        entity.snapshots[float_replicator(partial(getattr, data, 'z'), 'z')] = clock()
        entity.snapshots[string_replicator(partial(getattr, data, 'model'), 'model')] = clock()
        entity.snapshots[string_replicator(partial(data.material.get, 'map'), 'map')] = clock()


class Sprite(BaseComponent):
    data = {
        'sprite': 'textures/dev.png',
        'scale': 1.0,
        'z': 0.01,
        'anchor': {
            'x': 0.5,
            'y': 0.5
        },
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[float_replicator(partial(getattr, data, 'scale'), 'scale')] = clock()
        entity.snapshots[float_replicator(partial(getattr, data, 'z'), 'z')] = clock()
        entity.snapshots[float_replicator(partial(data['anchor'].get, 'x'), 'anchor_x')] = clock()
        entity.snapshots[float_replicator(partial(data['anchor'].get, 'y'), 'anchor_y')] = clock()
        entity.snapshots[string_replicator(partial(getattr, data, 'sprite'), 'sprite')] = clock()
