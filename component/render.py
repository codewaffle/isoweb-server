from component import BaseComponent


class Mesh(BaseComponent):
    _data = {
        'model': 'models/quad.json',
    }

class MeshMaterial(BaseComponent):
    _data = {
        'type': 'MeshLambertMaterial',
        'map': 'textures/dev.png',
    }