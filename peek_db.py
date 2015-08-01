import lmdb
from config import DB_DIR

db = lmdb.Environment('{}/{}'.format(DB_DIR, 0))

with db.begin() as tx:
    for x in tx.cursor():
        print x