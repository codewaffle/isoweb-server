from isoweb_time import clock
import lmdb
import ujson
import logbook
from component import c
from config import DB_DIR
from entity import Entity
from entitydef import definition_from_key
from mathx.quadtree import Quadtree

from scheduler import Scheduler


class Region:
    def __init__(self, region_id):
        self._delete_set = set()
        self.region_id = region_id
        self.scheduler = Scheduler()
        self.entities = set()
        self.quadtree = Quadtree()
        self._dirty_set = set()
        self.log = logbook.Logger('Island({})'.format(region_id))

        self.max_entity_id = None

        self.db = lmdb.Environment('{}/{}'.format(DB_DIR, self.region_id), map_size=1024*1024*64)

        with self.db.begin() as tx:
            self.load_data(tx.cursor())

        with self.db.begin(write=True) as tx:
            self.save_data(tx.cursor())

    # this property is mostly to prevent reassignment on accident.
    @property
    def dirty_set(self):
        return self._dirty_set
    
    @property
    def delete_set(self):
        return self._delete_set

    def load_data(self, cursor):
        d = cursor.get(b'region_data', '{}')
        data = ujson.loads(d)
        self.max_entity_id = data.get('max_entity_id', 0)

        self.load_entities(cursor)

    def save_data(self, write_cursor):
        write_cursor.put(b'region_data', ujson.dumps({
            u'max_entity_id': self.max_entity_id
        }).encode('utf8'))

    def start(self):
        self.scheduler.schedule(func=self.save_snapshot)
        self.scheduler.start()

    def next_entity_id(self):
        self.max_entity_id += 1
        return self.max_entity_id

    def spawn(self, entdef, components=None, pos=None, rot=None, replicate=True):
        if isinstance(entdef, (str, bytes)):
            entdef = definition_from_key(entdef)

        ent = Entity(self.next_entity_id())
        ent.entity_def = entdef
        ent.ob.flags = 0
        ent.set_region(self)

        if components:
            ent.add_components(components)

        if pos is not None:
            ent.add_component(c.Position, initialize=False, x=pos.x, y=pos.y, r=rot or 0)

        if replicate:
            ent.add_component(c.Replicated, initialize=False)

        ent.initialize()
        return ent

    def save_snapshot(self):
        start = clock()

        self.dirty_set.difference_update(self.delete_set)

        with self.db.begin(write=True) as tx:
            cur = tx.cursor()

            self.save_data(cur)

            for ent in self.dirty_set:
                ent.save_data(cur)

            for ent in self.delete_set:
                tx.delete(ent.get_db_key())

            self.log.info('Snapshot: saved={} deleted={} elapsed={}', len(self.dirty_set), len(self.delete_set), clock() - start)
            self.dirty_set.clear()
            self.delete_set.clear()

        return 5.0

    def load_entities(self, cur):
        self.log.debug('Loading entities from db')
        start = clock()
        if cur.set_range(b'ent-'):
            for key, val in cur:
                if not key.startswith(b'ent-'):
                    break

                data = ujson.loads(val)

                ent = Entity(data['id'])
                ent.entity_def = definition_from_key(data['entitydef'])
                ent.ob.flags = data['ob_flags']
                ent.set_region(self)
                ent.update_components(data.get('components', {}))
                ent.initialize()
        self.log.info('Loaded entities in {} seconds', clock() - start)

    def destroy_entity(self, ent):
        # reset Reference
        for comp in ent.component_iter():
            comp.destroy()
        ent.valid = False
        del ent._memo_cache
        ent._memo_cache = {}
        self.delete_set.add(ent)
        del Entity._registry[ent.id]
