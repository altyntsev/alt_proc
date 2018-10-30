import os
import sys
import yaml
import traceback
import time
import json
from datetime import datetime

path = os.path.dirname(__file__) + '/_libs'
if path not in sys.path:
    sys.path.append(path)

from alt.dict_ import dict_
import alt.time
import alt.mysql
import alt.cfg

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

class Proc(object):

    __metaclass__ = Singleton

    def __init__(self):

        self.host = alt.cfg.host()

        # DB
        db_name = 'alt_proc-%s' % self.host
        db_cfg = alt.cfg.secure('alt_proc').db
        self.db = alt.mysql.DB(db=db_name, user=db_cfg.user, pwd=db_cfg.pwd)

    def except_handler(self, exctype, err, tb):

        sys.excepthook = sys.__excepthook__
        traceback.print_exception(exctype, err, tb)
        tb = '\n'.join(traceback.format_tb(tb))
        self.fatal('Exception')

    def start(self):

        wd = os.getcwd().replace('\\','/')
        if wd.split('/')[-3]=='jobs':

            self.mode = 'DB'
            s = wd.split('/')
            iscript, self.job_id = int(s[-1][1:]), int(s[-2])
            self.alt_proc_wd = os.path.abspath(wd + '/../../../') + '/'
            self.errors = False
            self.stime = alt.time.now_iso()
            self.msgs = []

            self.job = self.db.sql("select * from jobs where id=%s", self.job_id)[0]
            self.task = self.db.sql("select * from tasks where id=%s", self.job.task_id)[0]
            if self.task.type=='EVENT':
                self.event = self.db.sql("select * from events where id=%s", self.job.event_id)[0]
            self.script = self.db.sql("select * from scripts where job_id=%s AND i=%s",
                                    (self.job_id, iscript))[0]

            if debug:
                self.db.sql("update tasks set status='DEBUG' where id=%s", self.task.id)
                self.db.sql("update jobs set status='RUN', mtime=now() where id=%s", self.job_id)
                self.db.sql("update scripts set status='RUN' where id=%s", self.script.id)

            self.run_id = self.script.run_id

            sys.excepthook = self.except_handler

        else:

            self.mode = 'ALONE'

    def exit(self, fatal=False, restart_after=None):

        print('Exit')

        if self.mode=='ALONE':
            sys.exit()

        proc_result = 'SUCCESS'
        if self.errors:
            proc_result = 'ERRORS'
        if fatal:
            proc_result = 'FATAL'

        msgs = json.dumps(self.msgs) if self.msgs else None

        sql = "update runs " \
              "set stime=%s, etime=%s, result=%s, restart_after=%s, msgs=%s " \
              "where id=%s"
        self.db.sql(sql, (self.stime, datetime.now(), proc_result, restart_after, msgs, self.run_id))

        sys.exit()

    def emit_event(self, task, key, **params):

        print('Emit Event', task, key, params)

        if not params:
            params = None
        tasks = self.db.sql("select id from tasks where name=%s", task)
        if not tasks:
            self.fatal('Unknown task name')
        task_id = tasks[0].id

        sql = "insert into events (task_id, key, params, ctime) values (%s,%s,%s, %s)"
        event_id = self.db.insert(sql, (task_id, key, params, datetime.now()))

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