from util import to_bytes


class MenuItem:
    def __init__(self):
        pass

_registry = {}

class MultipleDefaultMenuItems(RuntimeError):
    pass

class Menu:
    def __init__(self):
        _registry[id(self)] = self
        self.data = {}

    @property
    def id(self):
        return id(self)

    def update(self, data):
        if data:
            self.data.update({to_bytes(k): v for k,v in data.items()})

    def __iter__(self):
        for k,v in self.data.items():
            yield (to_bytes(k), v)

    def execute(self, action, *args):
        func = self.data.get(action, None)

        if func:
            func[1](*args)

        self.destroy()

    def execute_default(self, *args):
        if len(self) > 1:
            raise MultipleDefaultMenuItems
        else:
            self.execute(list(self.data.keys())[0], *args)
            self.destroy()

    def destroy(self):
        del _registry[id(self)]

    @classmethod
    def from_dict(cls, d):
        menu = cls()
        menu.data = d
        return menu

    def __len__(self):
        return len(self.data)
