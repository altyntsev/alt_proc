import os
import sys
import yaml
import traceback
import json
from datetime import datetime

from alt.dict_ import dict_
import alt.time
import alt.postgresql
import alt.cfg
import alt.system

try:
    __IPYTHON__
    debug = True
except:
    debug = False

def read_cfg(cfgfile):

    with open(cfgfile) as f:
        cfg = yaml.load(f)

    return dict_(cfg)

def utc_now_iso():

    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

def time_iso(dt):

    return dt.strftime('%Y-%m-%d %H:%M:%S')

class Singleton(type):

    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Script(object):

    __metaclass__ = Singleton

    def __init__(self):

        self.host = alt.cfg.host()
        self.alt_proc_cfg = alt.cfg.read_global('alt_proc')

        # DB
        if self.alt_proc_cfg.hub:
            host = alt.cfg.host()
            db_name = 'alt_proc-%s' % host
        else:
            db_name = 'alt_proc'
        db_cfg = alt.cfg.secure('alt_proc').db
        if not self.alt_proc_cfg.production:
            n_try = 1
        else:
            n_try = 10
        self.db = alt.postgresql.DB(db=db_name, user=db_cfg.user, pwd=db_cfg.pwd, n_try=n_try)

        self.mode = 'ALONE'

    def except_handler(self, exctype, err, tb):

        sys.excepthook = sys.__excepthook__
        traceback.print_exception(exctype, err, tb)
        tb = '\n'.join(traceback.format_tb(tb))
        self.fatal('Exception')

    def start(self):

        wd = os.getcwd().replace('\\','/')
        if wd.split('/')[-3]!='jobs':
            return

        self.mode = 'DB'
        s = wd.split('/')
        self.iscript, self.job_id = int(s[-1][1:]), int(s[-2])
        self.alt_proc_wd = os.path.abspath(wd + '/../../../') + '/'
        self.errors = False
        self.msgs = []

        sql = """
            select r.id as run_id, e.param, e.params, t.id as task_id, s.id as script_id, 
                r.debug, t.project, s.cmd, s.status, j.os_pid
            from tasks t 
            join events e on t.id = e.task_id
            join jobs j on j.event_id=e.id  
            join scripts s on s.job_id=j.id
            left join runs r on s.last_run_id = r.id
            where j.id=%s and s.iscript=%s
        """
        row, = self.db.sql(sql, (self.job_id, self.iscript))
        self.task_id, self.run_id, self.script_id = row.task_id, row.run_id, row.script_id
        self.project, self.cmd = row.project, row.cmd
        self.event = dict_(param=row.param, params=row.get('params', dict_()))

        if debug and not row.debug and row.status=='RUN':
            if alt.system.process_exists(row.os_pid):
                raise Exception('Script is running')

        if not debug or (debug and row.run_id is None):
            sql = """
                insert into runs (script_id, debug) values (%s, %s) 
                """
            self.run_id = self.db.sql(sql, (self.script_id, debug))
            sql = """
                update scripts set last_run_id=%s where id=%s
                """
            self.db.sql(sql, (self.run_id, self.script_id))
        sql = """
            update runs set stime=now(), debug=%s where id=%s 
            """
        self.db.sql(sql, (debug, self.run_id))

        self.db.sql("update jobs set status='RUN' where id=%s", self.job_id)
        self.db.sql("update scripts set status='RUN', last_run_id=%s where id=%s",
                    (self.run_id, self.script_id))
        if debug:
            self.db.sql("update tasks set status='DEBUG' where id=%s", self.task_id)

        print('Script ', self.project, ':', self.cmd, 'started')

        sys.excepthook = self.except_handler

    def exit(self, fatal=False, restart_after=None):

        if self.mode=='ALONE':
            sys.exit()

        result = 'SUCCESS'
        if self.errors:
            result = 'ERRORS'
        if fatal:
            result = 'FATAL'

        msgs = json.dumps(self.msgs) if self.msgs else None

        sql = """
            update runs 
            set etime=now(), result=%s, restart_after=%s, msgs=%s 
            where id=%s
            """
        self.db.sql(sql, (result, restart_after, msgs, self.run_id))

        print('Script ', self.project, ':', self.cmd, 'finished')

        sys.exit()

    def emit_event(self, task, param, **params):

        print('Emit Event', task, param, params)

        if not params:
            params = None
        tasks = self.db.sql("select id from tasks where name=%s", task)
        if not tasks:
            self.fatal('Unknown task name')
        task_id = tasks[0].id

        sql = "insert into events (task_id, param, params) VALUES (%s,%s,%s)"
        event_id = self.db.sql(sql, (task_id, param, params))

        return event_id

    def msg(self, msg_type, msg_str, data=None):

        print(msg_type, msg_str, data)

        if self.mode=='DB':
            msg = dict_(type=msg_type, msg=str(msg_str))
            if data:
                msg.data = data
            self.msgs.append( msg )
            print(msg)

    def fatal(self, msg, restart_after=None, **kwds):

        self.msg('FATAL', msg, kwds)

        self.exit(fatal=True, restart_after=restart_after)

    def error(self, msg, **kwds):

        self.msg('ERROR', msg, kwds)

    def success(self):

        self.exit()