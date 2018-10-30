import psycopg2
import psycopg2.extras
import time
from alt.dict_ import dict_

class DB:

    def __init__(self, host='127.0.0.1', user=None, pwd=None, db=None, n_try=10):

        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.n_try = n_try
        self.connect()

    def connect(self):

        # print('Connect')
        itry = 1
        while True:
            try:
                self.conn = psycopg2.connect(host=self.host, user=self.user, password=self.pwd,
                                             database=self.db)
                self.conn.autocommit = True
                break
            except psycopg2.OperationalError:
                if itry==self.n_try:
                    raise
                print('OperationalError', itry)
            itry += 1
            time.sleep(1)

    def sql(self, sql, params=None, return_id=True):

        if not isinstance(params, (tuple, list)):
            params = (params,)
        # print(sql, params)
        itry = 1
        while True:
            try:
                cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                if return_id and sql.strip().lower().startswith('insert'):
                    sql += ' RETURNING id'
                cur.execute(sql, params)
                if sql.strip().lower().startswith('select'):
                    data = [dict_(row) for row in cur.fetchall()]
                    return data
                if return_id and sql.strip().lower().startswith('insert'):
                    return cur.fetchone()[0]
                break
            except psycopg2.OperationalError:
                if itry==self.n_try:
                    raise
                print('OperationalError', itry)
                self.connect()
            itry += 1
            time.sleep(1)

