import alt_path
from _header import *

def connect():

    pwd_file = alt.cfg.read_global('alt_proc').pwd_file
    pwd = alt.cfg.read(pwd_file).db.pwd
    db = alt.pg.DB(db='alt_proc', user='alt_proc', pwd=pwd, schema='alt_proc')

    return db

class Values:

    def __init__(self, db):

        self.db = db

    def __getitem__(self, name):

        rows = self.db.sql("select value from values where name=%s", name)

        return rows[0].value

    def __setitem__(self, name, value):

        self.db.sql("update values set value=%s where name=%s", (value, name))

