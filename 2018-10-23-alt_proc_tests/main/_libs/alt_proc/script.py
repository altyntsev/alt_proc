import os
import sys
import yaml
import traceback
import json
import re
from datetime import datetime

from alt.dict_ import dict_
import alt.time
import alt.pg
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

class _Singleton(type):

    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(_Singleton('SingletonMeta', (object,), {})):

    pass

class Script(Singleton):

    def __init__(self):

        self.host = alt.cfg.host()
        self.alt_proc_cfg = alt.cfg.read_global('alt_proc')

        # DB
        pwd_file = alt.cfg.read_global('alt_proc').pwd_file
        pwd = alt.cfg.read(pwd_file).db.pwd
        self.db = alt.pg.DB(db='alt_proc', user='alt_proc', pwd=pwd, schema='alt_proc')

        self.mode = 'ALONE'

    def except_handler(self, exctype, err, tb):

        sys.excepthook = sys.__excepthook__
        traceback.print_exception(exctype, err, tb)
        tb = '\n'.join(traceback.format_tb(tb))
        self.fatal('Exception')

    def start(self):

        wd = os.getcwd().replace('\\','/')
        m = re.match('(.+)/jobs/(\d*)/_(\d*)', wd)
        if not m:
            return
        self.mode = 'DB'
        self.alt_proc_wd, self.job_id, self.iscript = m.groups()
        self.alt_proc_wd = self.alt_proc_wd + '/'
        self.job_id = int(self.job_id)
        self.iscript = int(self.iscript)
        self.errors = False
        self.msgs = []

        sql = """
            select r.run_id, e.param, e.params, t.task_id, s.script_id, 
                r.debug, t.project, s.cmd, s.status, j.os_pid
            from tasks t 
            join events e on t.task_id = e.task_id
            join jobs j on j.event_id=e.event_id  
            join scripts s on s.job_id=j.job_id
            left join runs r on s.last_run_id = r.run_id
            where j.job_id=%s and s.iscript=%s
        """
        row, = self.db.sql(sql, (self.job_id, self.iscript))
        self.task_id, self.run_id, self.script_id = row.task_id, row.run_id, row.script_id
        self.project, self.cmd = row.project, row.cmd
        self.event = dict_(param=row.param, params=row.get('params', dict_()))

        if debug and not row.debug and row.status=='RUN':
            if alt.system.process_running(row.os_pid):
                raise Exception('Script is running')

        if not debug or (debug and row.run_id is None):
            sql = """
                insert into runs (script_id, debug) values (%s, %s) 
                """
            self.run_id = self.db.sql(sql, (self.script_id, debug), return_id='run_id')
            sql = """
                update scripts set last_run_id=%s where script_id=%s
                """
            self.db.sql(sql, (self.run_id, self.script_id))
        sql = """
            update runs set stime=now(), debug=%s where run_id=%s 
            """
        self.db.sql(sql, (debug, self.run_id))

        self.db.sql("update jobs set status='RUN' where job_id=%s", self.job_id)
        self.db.sql("update scripts set status='RUN', last_run_id=%s where script_id=%s",
                    (self.run_id, self.script_id))
        if debug:
            self.db.sql("update tasks set status='DEBUG' where task_id=%s", self.task_id)

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
            set etime=now(), result = %s, restart_after = %s, msgs = %s 
            where run_id=%s
            """
        self.db.sql(sql, (result, restart_after, msgs, self.run_id))

        print('Script ', self.project, ':', self.cmd, 'finished')
        if restart_after:
            print('restart_after = %s' % restart_after)

        sys.exit()

    def emit_event(self, task, param, **params):

        print('Emit Event', task, param, params)

        if not params:
            params = None
        sql = "select task_id from tasks where name=%s and status!='DELETED'"
        tasks = self.db.sql(sql, task)
        if not tasks:
            self.fatal('Unknown task name')
        task_id = tasks[0].task_id

        sql = "insert into events (task_id, param, params) VALUES (%s,%s,%s)"
        event_id = self.db.sql(sql, (task_id, param, params), return_id='event_id')

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