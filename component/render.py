from functools import partial
from time import clock

from component import BaseComponent
from component.base import component_method
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

    @component_method
    def initialize(self):
        self.entity.snapshots[float_replicator(partial(getattr, self.data, 'scale'), 'scale')] = clock()
        self.entity.snapshots[float_replicator(partial(getattr, self.data, 'z'), 'z')] = clock()
        self.entity.snapshots[string_replicator(partial(getattr, self.data, 'model'), 'model')] = clock()
        self.entity.snapshots[string_replicator(partial(self.data.material.get, 'map'), 'map')] = clock()


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

    @component_method
    def initialize(self):
        self.entity.snapshots[float_replicator(partial(getattr, self.data, 'scale'), 'scale')] = clock()
        self.entity.snapshots[float_replicator(partial(getattr, self.data, 'z'), 'z')] = clock()
        self.entity.snapshots[float_replicator(partial(self.data['anchor'].get, 'x'), 'anchor_x')] = clock()
        self.entity.snapshots[float_replicator(partial(self.data['anchor'].get, 'y'), 'anchor_y')] = clock()
        self.entity.snapshots[string_replicator(partial(getattr, self.data, 'sprite'), 'sprite')] = clock()
