from entity import Entity


class Tree(Entity):
    client_class = 'SimpleSprite'

    _class_attributes = Entity.subclass_attributes({
        'sprite': ('s', 'sprites/blobby_tree_bush_thing.png')
    })
