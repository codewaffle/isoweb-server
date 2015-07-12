from component import BaseComponent



class CharacterController(BaseComponent):
    pass



class Transform(BaseComponent):
    _data = {
        'x': 1,
        'y': 2
    }

    @classmethod
    def teleport(cls, entity, data, x, y):
        data.x = x
        data.y = y
        print 'ok!'

