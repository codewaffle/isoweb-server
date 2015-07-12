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
    defaults = {
        'capacity': 0
    }

class Melee(BaseComponent):
    pass

class Craftable(BaseComponent):
    pass

class Hammer(BaseComponent):
    defaults = {
        'beat': 12
    }

    @classmethod
    def beat(cls, entity, data):
        print entity
        print data
        data.beats += 1
        return 'beat return', data.beats

class Foliage(BaseComponent):
    pass
