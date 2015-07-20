from functools import partial
from time import time
from component import BaseComponent
from component.base import string_replicator

class Mesh(BaseComponent):
    data = {
        'model': 'models/quad.json',
        'material': {
            'type': 'MeshLambertMaterial',
            'map': 'textures/dev.png',
        }
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[string_replicator(partial(getattr, data, 'model'), 'model')] = time()
        entity.snapshots[string_replicator(partial(data.material.get, 'map'), 'map')] = time()

class Sprite(BaseComponent):
    data = {
        'sprite': 'sprites/null.png'
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[string_replicator(partial(getattr, data, 'sprite'), 'sprite')] = time()
