from entity import Entity


class Tree(Entity):
    _class_attributes = Entity._class_attributes.copy()
    _attributes['sprite'] = 'sprites/blobby_tree_bush_thing.png'
