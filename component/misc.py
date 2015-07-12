from component import BaseComponent


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