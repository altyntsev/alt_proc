from header import *

class DB:

    def __init__(self):

        cfg = alt.cfg.read()

        if not cfg.production:
            user, pwd, n_try = 'alt_proc', 'alt_proc', 1

        self.dbs = {}

        if not cfg.hub:
            hosts = ['localhost']
        for host in hosts:
            if host=='localhost':
                db_name = 'alt_proc'
            db = alt.postgresql.DB(db=db_name, user=user, pwd=pwd)
            self.dbs[host] = db

    def get(self, host):

        return self.dbs[host]


