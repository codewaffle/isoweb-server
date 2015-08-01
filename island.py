from time import clock
from gevent import Greenlet
import lmdb
import ujson
import logbook
from component import c
from config import DB_DIR
from entity import Entity, ObFlags, SnapshotContainer
from entitydef import definition_from_key
from mathx import Quadtree

from scheduler import Scheduler


class Island(Greenlet):
    def __init__(self, island_id):
        super(Island, self).__init__()
        self.island_id = island_id
        self.scheduler = Scheduler()
        self.entities = set()
        self.entities_by_id = {}
        self.quadtree = Quadtree()
        self._dirty_set = set()
        self.log = logbook.Logger('Island({})'.format(island_id))

        self.max_entity_id = None

        self.db = lmdb.Environment('{}/{}'.format(DB_DIR, self.island_id))

        with self.db.begin() as tx:
            self.load_data(tx.cursor())

        with self.db.begin(write=True) as tx:
            self.save_data(tx.cursor())

    # this property is mostly to prevent reassignment on accident.
    @property
    def dirty_set(self):
        return self._dirty_set

    def load_data(self, cursor):
        data = ujson.loads(cursor.get('island_data', "{}"))
        self.max_entity_id = data.get('max_entity_id', 0)

        self.load_entities(cursor)

    def save_data(self, write_cursor):
        write_cursor.put('island_data', ujson.dumps({
            'max_entity_id': self.max_entity_id
        }))

    def _run(self):
        self.scheduler.start()
        self.scheduler.schedule(func=self.save_snapshot)
        self.scheduler.join()

    def next_entity_id(self):
        self.max_entity_id += 1
        return self.max_entity_id

    def spawn(self, entdef, components=None, pos=None, rot=None, ob_flags=ObFlags.REPLICATE):
        if isinstance(entdef, basestring):
            entdef = definition_from_key(entdef)

        ent = Entity(self.next_entity_id())
        ent.entity_def = entdef
        ent.ob.flags = ob_flags
        ent.set_island(self)

        if components:
            ent.add_components(components)

        if pos is not None:
            ent.add_component(c.Position, initialize=False, x=pos.x, y=pos.y, r=rot or 0)

        ent._frozen = True
        ent.initialize()
        return ent.reference

    def get_entity(self, ent_id):
        return self.entities_by_id[ent_id]

    def save_snapshot(self):
        self.log.debug('Saving snapshot to db')
        start = clock()
        with self.db.begin(write=True) as tx:
            cur = tx.cursor()

            self.save_data(cur)

            for ent in self.dirty_set:
                ent.save_data(cur)

            self.dirty_set.clear()
        self.log.info('Saved snapshot in {} seconds', clock() - start)

        return -5.0

    def load_entities(self, cur):
        self.log.debug('Loading entities from db')
        start = clock()
        if cur.set_range('ent-'):
            for key, val in cur:
                if not key.startswith('ent-'):
                    break

                data = ujson.loads(val)

                ent = Entity(data['id'])
                ent.entity_def = definition_from_key(data['entitydef'])
                ent.ob.flags = data['ob_flags']
                ent.set_island(self)
                ent.update_components(data.get('components', {}))
                ent._frozen = True
                ent.initialize()
        self.log.info('Loaded entities in {} seconds', clock() - start)