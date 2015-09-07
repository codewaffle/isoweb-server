from component import BaseComponent


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


class Spine(BaseComponent):
    data = {
        'atlas': 'SPINE_ATLAS_NOT_SET',
        'character': 'SPINE_CHARACTER_NOT_SET',
        'scale': 1.0
    }

    exports = ['atlas', 'character', 'scale']
