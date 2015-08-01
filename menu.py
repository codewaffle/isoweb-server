class MenuItem(object):
    def __init__(self):
        pass

_registry = {}

class MultipleDefaultMenuItems(RuntimeError):
    pass

class Menu(object):
    def __init__(self):
        _registry[id(self)] = self
        self.data = {}

    @property
    def id(self):
        return id(self)

    def update(self, data):
        self.data.update(data)

    def __iter__(self):
        for x in self.data.iteritems():
            yield x

    def execute(self, action, *args):
        func = self.data.get(action, None)

        if func:
            func[1](*args)

    def execute_default(self, *args):
        if len(self) > 1:
            raise MultipleDefaultMenuItems
        else:
            self.execute(self.data.keys()[0], *args)

    @classmethod
    def from_dict(cls, d):
        menu = cls()
        menu.data = d
        return menu

    def __len__(self):
        return len(self.data)