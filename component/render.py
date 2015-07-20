from functools import partial
from time import time
from component import BaseComponent
from component.base import string_replicator
import packet_types


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
        entity.snapshots[entity.Mesh.mesh_update] = time()

    @classmethod
    def mesh_update(cls, entity, data):
        if data.material['type'] == 'MeshLambertMaterial':
            mat_type = 1
        else:
            mat_type = 124

        model_len = len(data.model)
        map_len = len(data.material['map'])

        return 'HBB{}sB{}s'.format(
            model_len, map_len
        ), [
            packet_types.MESH_UPDATE, mat_type, model_len, data.model, map_len, data.material['map']
        ]

class Sprite(BaseComponent):
    data = {
        'sprite': 'sprites/null.png'
    }

    @classmethod
    def initialize(cls, entity, data):
        entity.snapshots[string_replicator(partial(getattr, data, 'sprite'), 'sprite')] = time()
