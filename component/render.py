from functools import partial
from isoweb_time import clock

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
    exports = ['model', 'scale', 'material']

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
    exports = [
        'scale', 'sprite', 'anchor'
    ]
