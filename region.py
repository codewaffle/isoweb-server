from isoweb_time import clock
from collections import defaultdict
import lmdb
import ujson
import logbook
import component
from config import DB_DIR
from entity import Entity
from entitydef import definition_from_key, EntityDef
from phys.space import PhysicsSpace
from scheduler import Scheduler


def component_dict(*args):
    return defaultdict(dict, *args)


class Region:
    def __init__(self, region_id, load=True):
        self.space = PhysicsSpace(None)
        self._delete_set = set()
        self.region_id = region_id
        self.scheduler = Scheduler()
        self.entities = set()
        self._dirty_set = set()
        self.log = logbook.Logger('Island({})'.format(region_id))

        self.max_entity_id = 0

        self.db = lmdb.Environment('{}/{}'.format(DB_DIR, self.region_id), map_size=1024*1024*64)

        if load:
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
        self.scheduler.schedule(func=self.simulate)
        self.scheduler.start()

    def simulate(self):
        self.space.step(1/20.0)
        return -1/20.0

    def next_entity_id(self):
        self.max_entity_id += 1
        return self.max_entity_id

    def spawn(self,
              entity_def,
              parent=None,
              spawn_components
              =None,
              pos=None,
              rot=None,
              replicate=True,
              ent_id=None):
        if isinstance(entity_def, (str, bytes)):
            entity_def = definition_from_key(entity_def)

        assert isinstance(entity_def, EntityDef)

        if ent_id is None:
            ent_id = self.next_entity_id()

        ent = Entity(ent_id)
        ent.entity_def = entity_def
        ent.parent = parent
        ent.set_region(self)

        entity_def_components = {k.__name__: v for k, v in entity_def.component_data.items()}
        if entity_def_components:
            ent.add_components(entity_def_components, initialize=False, entity_def=entity_def)

        # gather up components from various sources
        components = component_dict()
        if isinstance(spawn_components, (list, tuple, set)):
            for comp_name in spawn_components:
                components[comp_name].update()  # trigger defaultdict creation
        elif isinstance(spawn_components, dict):
            for comp_name, comp_init in spawn_components.items():
                components[comp_name].update(comp_init)

        if pos is not None:
            components['Position'].update({'x': pos.x, 'y': pos.y, 'r': rot or 0})

        if replicate:
            components['Replicated'].update()

        if components:
            ent.add_components(components, initialize=False)

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
        count = 0
        if cur.set_range(b'ent-'):
            for key, val in cur:
                if not key.startswith(b'ent-'):
                    break

                data = ujson.loads(val)

                ent = self.spawn(
                    data['entitydef'],
                    spawn_components=data.get('components', {}),
                    replicate=False, # set by Replicate component
                    ent_id=data['id']
                )

                # ent.ob.flags = data['ob_flags']
                count += 1
                
        self.log.info('Loaded {} entities in {} seconds', count, clock() - start)

    def destroy_entity(self, ent):
        # reset Reference
        for comp in ent.component_iter():
            comp.destroy()
        ent.valid = False
        del ent._memo_cache
        ent._memo_cache = {}
        self.delete_set.add(ent)
        del Entity._registry[ent.id]
