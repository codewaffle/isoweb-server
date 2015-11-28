from component import BaseComponent


class Mesh(BaseComponent):
    model = 'models/quad.json'
    scale = 1.0
    z = 0.01
    material = {
       'type': 'MeshLambertMaterial',
       'map': 'textures/dev.png',
    }
    
    exports = ['model', 'scale', 'material']


class Sprite(BaseComponent):
    sprite = 'textures/dev.png'
    scale = 1.0
    z = 0.01
    anchor = {
        'x': 0.5,
        'y': 0.5
    }

    exports = [
        'scale', 'sprite', 'anchor'
    ]
    
    def __init__(self, ent, entity_def):
        if 'value' in entity_def:
            entity_def['sprite'] = entity_def['value']
            del entity_def['value']
        super(Sprite, self).__init__(ent, entity_def)

    @property
    def value(self):
        return self.sprite

    @value.setter
    def value(self, value):
        self.sprite = value


class Spine(BaseComponent):
    atlas = 'SPINE_ATLAS_NOT_SET'
    character = 'SPINE_CHARACTER_NOT_SET'
    scale = 1.0

    exports = ['atlas', 'character', 'scale']
