from gevent import Greenlet
from entity import Entity
from entitydef import definition_from_key
from quadtree import Quadtree

from scheduler import Scheduler


class Island(Greenlet):
    def __init__(self):
        super(Island, self).__init__()
        self.scheduler = Scheduler()
        self.entities = set()
        self.quadtree = Quadtree()

    def _run(self):
        self.scheduler.start()
        self.scheduler.schedule(func=self.update)
        self.scheduler.join()

    def update(self, dt):
        # print 'updated in', dt
        return 1/20.

    def spawn(self, entdef, components=None):
        if isinstance(entdef, basestring):
            entdef = definition_from_key(entdef)

        ent = Entity(entdef)

        if isinstance(components, list):
            for comp_class in components:
                setattr(ent, comp_class.__name__, comp_class.bind(ent, False))
        elif isinstance(components, dict):
            for comp_class, data in components.items():
                comp = comp_class.bind(ent, False)
                setattr(ent, comp_class.__name__, comp)
                comp.data.update(data)

        self.entities.add(ent)
        ent.island = self

        ent._frozen = True
        ent.initialize()
        return ent.reference
