from component.base import BaseComponent

class EquipmentUser(BaseComponent):
    pass

class Chopper(BaseComponent):
    pass

class Choppable(BaseComponent):
    pass

class Containable(BaseComponent):
    pass

class Equippable(BaseComponent):
    pass

class Container(BaseComponent):
    _data = {
        'capacity': 0
    }

class Melee(BaseComponent):
    pass

class Craftable(BaseComponent):
    pass

class Hammer(BaseComponent):
    pass

class Foliage(BaseComponent):
    pass

class CharacterController(BaseComponent):
    pass

class Mesh(BaseComponent):
    _data = {
        'model': 'models/quad.json',
    }

class MeshMaterial(BaseComponent):
    _data = {
        'type': 'MeshLambertMaterial',
        'map': 'textures/dev.png',
    }
