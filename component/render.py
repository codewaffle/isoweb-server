from component import BaseComponent


class Mesh(BaseComponent):
    data = {
        'model': 'models/quad.json',
        'material': {
            'type': 'MeshLambertMaterial',
            'map': 'textures/dev.png',
        }
    }
