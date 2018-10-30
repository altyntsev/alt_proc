import alt_path
from header import *

def connect():

    cfg = alt.cfg.read()
    if cfg.hub:
        host = alt.cfg.host()
        db_name = 'alt_proc-%s' % host
    else:
        db_name = 'alt_proc'
    db_cfg = alt.cfg.secure('alt_proc').db
    if not cfg.production:
        n_try = 1
    else:
        n_try = 10
    db = alt.postgresql.DB(db=db_name, user=db_cfg.user, pwd=db_cfg.pwd, n_try=n_try)

    return db

class Values:

    def __init__(self, db):

        self.db = db

    def __getitem__(self, name):

        rows = self.db.sql("select value from values where name=%s", name)

        return rows[0].value

    def __setitem__(self, name, value):

        self.db.sql("update values set value=%s where name=%s", (value, name))

