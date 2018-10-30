import alt_path
from header import *
import db_lib

class Msg_processor:

    def __init__(self, root):

        self.root = root
        self.refresh()

    def refresh(self):

        sql = "select value from key_values where key='cfg_msgs'"
        text = self.root.db.sql(sql)[0].value
        self.cfg = []
        for i, line in enumerate(text.split('\n')):
            if not line.strip():
                continue
            m = re.match('([+-] *(.+?) *(.+?) *\"(.+?)\" *(.*))', line)
            if not m:
                raise Exception('Wrong format in line %s' % (i+1))
            todo, task, script, msg, delay = m.groups()
            task, script, msg = task.replace('*','.+'), script.replace('*','.+'), msg.replace('*','.+')
            todo = todo=='+'
            if delay:
                delay = float(delay)
            else:
                delay = 0
            self.cfg.append( dict_(todo=todo, task=task, script=script, msg=msg, delay=delay))

    def todo(self, msg, task, job, script, run):

        todo = msg.type in ['FATAL','ERROR']
        now = datetime.now()

        for cfg in self.cfg:
            if cfg.delay:
                if 'stime' in msg and now-msg.stime > timedelta(hours=cfg.delay):
                    print('delay')
                    continue
            if not re.match(cfg.task, task.name):
                continue
            if not re.match(cfg.script, script.cmd):
                continue
            if not re.match(cfg.msg, msg.msg):
                continue
            todo = cfg.todo

        return todo

    def run_done(self, task, job, script, run):

        sql = "select * from msgs where job_id=%s AND active"
        existing_msgs = self.root.db.sql(sql, job.id)
        todo = False

        run.msgs = [dict_(msg) for msg in json.loads(run.msgs)] if run.msgs else []

        obsolete_msg_ids = [msg.id for msg in existing_msgs]
        for msg in run.msgs:
            for existing_msg in existing_msgs:
                if existing_msg.proc_id==script.id and existing_msg.msg==msg.msg: # same msg
                    todo = self.todo(existing_msg, task, job, script, run)
                    print(msg.msg, todo)
                    existing_msg.etime = run.etime
                    existing_msg.n_runs += 1
                    self.root.db.sql("update msgs set etime=%s, n_runs=%s, todo=%s where id=%s",
                                    (existing_msg.etime, existing_msg.n_runs, todo, existing_msg.id))
                    obsolete_msg_ids.remove(existing_msg.id)
                    break
            else: # new msg
                todo = self.todo(msg, task, job, script, run)
                self.root.db.sql("insert into msgs (msg, type, job_id, proc_id, stime, etime, todo)"
                                 "values (%s,%s,%s,%s,%s,%s,%s)",
                                 (msg.msg, msg.type, job.id, script.id, run.stime, run.etime, todo))

        # obsolete
        for msg_id in obsolete_msg_ids:
            self.root.db.sql("update msgs set active=0, todo=%s where id=%s", (todo, msg_id))

        return todo

class Resources:

    def __init__(self, mgr):

        self.mgr = mgr
        self.reload()

    def reload(self):

        self.resources = dict_(json.loads(self.mgr.values['cfg_resources']))
        sql = """
            select name, n_runs from tasks 
        """
        tasks = self.mgr.db.sql(sql)
        for task in tasks:
            self.resources['n_runs-' + task.name] = task.n_runs

    def new_loop(self):

        self.loop_resources = dict_(self.resources)

    def use(self, task_name, task_resources):

        self.loop_resources['n_runs-' + task_name] -= 1

    def available(self, task_name, task_resources):

        if self.loop_resources['n_runs-' + task_name] <= 0:
            return False

        return True

class Manager:

    def __init__(self):

        self.cfg = alt.cfg.read()
        self.root_dir = alt.file.abspath(alt.cfg.projects_dir() + '..')
        self.main_dir = alt.cfg.main_dir()
        self.host = alt.cfg.host()
        wd = alt.file.wd()
        if wd.split('/')[-2]!='manager':
            raise Exception('Wrong working directory')
        self.alt_proc_wd = alt.file.abspath(wd + '../')
        self.db = db_lib.connect()
        # self.msg_processor = Msg_processor(self)
        self.values = db_lib.Values(self.db)

        host_status = self.values['host_status']

        if host_status=='EXIT':
            self.values['host_status'] = 'RUN'

        self.resources = Resources(self)
        self.cmds()
        self.periodic_init()

        print('ALT_Processing manager started', datetime.now())

    def periodic_init(self):

        print('periodic_init')
        # new periodic tasks
        sql = """
            select t.id from tasks t
            left join events e on t.id = e.task_id 
            where t.type='PERIODIC' and t.status='ACTIVE' and e.id is null 
            """
        tasks = self.db.sql(sql)
        for task in tasks:
            sql = "insert into events (task_id, status) values (%s,%s)"
            event_id = self.db.sql(sql, (task.id,'USED'))
            self.create_job(event_id)

    def process_events(self):

        sql = """
            select e.id, t.name as task, t.resources 
            from tasks t 
            join events e on t.id = e.task_id
            where t.type='EVENT' and t.status='ACTIVE' and e.status='WAIT'  
            order by priority
            """
        events = self.db.sql(sql)
        for event in events:
            if not self.resources.available(event.task, event.resources):
                continue
            self.create_job(event.id)
            sql = "update events set status='USED' where id=%s"
            self.db.sql(sql, event.id)
            return True
        return False


    def create_job(self, event_id):

        sql = """
            select t.name, t.project from tasks t
            left join events e on e.task_id=t.id
            where e.id=%s
            """
        task, = self.db.sql(sql, event_id)
        task_file = '%s/projects/%s/main/_cfg/%s.task' % \
                (self.root_dir, task.project, task.name)
        task_cfg = alt.cfg.read(task_file)
        sql = "insert into jobs (event_id, mtime) values (%s, now())"
        job_id = self.db.sql(sql, event_id)
        job_wd = self.alt_proc_wd + 'jobs/%s/' % job_id
        for iscript, script in enumerate(task_cfg.scripts):
            sql = "insert into scripts (job_id, iscript, cmd, name) values (%s,%s,%s,%s)"
            self.db.sql(sql, (job_id, iscript, script.cmd, alt.file.name(script.cmd)))
            script_wd = job_wd + '_{0:02d}/'.format(iscript)
            alt.file.mkdir(script_wd)
            script_cmd = '%s/projects/%s/main/%s' % \
                       (self.root_dir, task.project, script.cmd)
            alt.file.write(script_wd + 'run.cfg', alt.file.abspath(script_cmd))

    def inspect_running_jobs(self):

        sql = """
            select t.name as task, r.result, s.id as script_id, j.id as job_id,
                r.restart_after, t.type, t.period, t.resources, t.project, s.cmd
            from jobs j
            join events e on j.event_id = e.id
            join tasks t on e.task_id = t.id
            join scripts s on j.id = s.job_id
            left join runs r on s.last_run_id=r.id
            where j.status='RUN' and s.status='RUN' and t.status!='DEBUG'
        """
        jobs = self.db.sql(sql)
        for job in jobs:

            if job.result is None: # script is working
                self.resources.use(job.task, job.resources)
                continue

            print('Script', job.project, ':', job.cmd, 'finished')
            if job.restart_after: # restart
                sql = "update scripts set status='WAIT', result=%s where id=%s"
                self.db.sql(sql, (job.result, job.script_id))
                sql = """
                    update jobs 
                    set status='WAIT', run_at=now() + INTERVAL '%s minute', mtime=now() 
                    where id=%s
                    """
                self.db.sql(job.restart_after, sql, job.job_id)
                continue

            # script done
            sql = "update scripts set status='DONE', result=%s where id=%s"
            self.db.sql(sql, (job.result, job.script_id))
            sql = "update jobs set status='WAIT', mtime=now() where id=%s"
            self.db.sql(sql, job.job_id)

            # job done?
            sql = """
                select s.status, s.result
                from scripts s 
                join jobs j on s.job_id = j.id
                where j.id=%s
            """
            scripts = self.db.sql(sql, (job.job_id))
            job_status, job_result = 'DONE', 'SUCCESS'
            for script in scripts:
                if script.status!='DONE':
                    job_status = script.status
                if script.result=='FATAL':
                    job_result = 'FATAL'
                if job_result=='SUCCESS' and script.result=='ERRORS':
                    job_result = 'ERRORS'
            if job_status!='DONE':
                continue

            # job done!
            if job.type=='PERIODIC':
                sql = """
                    update jobs 
                    set status='WAIT', run_at=now() + INTERVAL '%s minute', result=%s, mtime=now() 
                    where id=%s
                    """
                self.db.sql(sql, (job.period, job_result, job.job_id))
                sql = """
                    update scripts
                    set status='WAIT' 
                    from scripts s
                    join jobs j on s.job_id=j.id
                    where scripts.id=s.id and j.id=%s 
                """
                self.db.sql(sql, (job.job_id))
            else:
                sql = "update jobs set status='DONE', result=%s, mtime=now() where id=%s"
                self.db.sql(sql, (job_result, job.job_id))

    def choose_job_to_run(self):

        sql = """
            select j.id, t.name as task, t.resources 
            from jobs j 
            join events e on j.event_id = e.id
            join tasks t on e.task_id = t.id
            where t.status='ACTIVE' and j.status='WAIT' and 
                (j.run_at is null or j.run_at<now()) 
            order by t.priority, j.ctime desc
            """
        jobs = self.db.sql(sql)

        for job in jobs:
            if not self.resources.available(job.task, job.resources):
                continue

            self.start_job(job.id)
            return True

        return False

    def start_job(self, job_id):

        sql = """
            select s.id, s.iscript, s.cmd, t.project
            from scripts s 
            join jobs j on s.job_id = j.id
            join events e on j.event_id = e.id
            join tasks t on e.task_id = t.id
            where j.id=%s and s.status='WAIT'
            order by s.iscript
            limit 1
        """
        script, = self.db.sql(sql, job_id)

        job_wd = self.alt_proc_wd + 'jobs/%s/' % job_id
        script_wd = job_wd + '_{0:02d}/'.format(script.iscript)
        alt.file.mkdir(script_wd)
        script_cmd = '%s/projects/%s/main/%s' % \
                   (self.root_dir, script.project, script.cmd)
        script_cmd = alt.file.abspath(script_cmd)
        alt.file.write(script_wd + 'run.cfg', script_cmd)

        cmd = '%s %s >>log.txt 2>&1' % (sys.executable, script_cmd)
        if os.name=='posix':
            cmd = cmd.split(' ')
        print('Script', script.project, ':', script.cmd, 'started')
        os_pid = subprocess.Popen(cmd, cwd=script_wd, shell=True).pid

        sql = "update jobs set status='RUN', os_pid=%s, mtime=now() where id=%s"
        self.db.sql(sql, (os_pid, job_id))
        sql = """
            update scripts
            set status='RUN'
            from scripts s
            join jobs j on s.job_id=j.id
            where scripts.id=s.id and j.id=%s and s.iscript=%s
        """
        self.db.sql(sql, (job_id, script.iscript))

    def cmds(self):

        for cmd in self.db.sql("select * from cmds where status='WAIT'"):
            print('CMD = ', cmd.name)

            error = None
            params = cmd.params
            try:

                if cmd.name == 'NEW_TASK':
                    task = params
                    if self.db.sql("select * from tasks where name=%s", task.name):
                        raise Exception('Task name exists')
                    if task.type=='PERIODIC':
                        sql = "insert into tasks (name, type, project, job, period, priority) "\
                              "values (%s,%s,%s,%s,%s,%s)"
                        self.db.sql(sql, (task.name, task.type, task.project, task.job, task.period, task.priority))
                    elif task.type=='EVENT':
                        sql = "insert into tasks (name, type, project, job, priority, n_fatals, n_runs) "\
                              "values (%s,%s,%s,%s,%s,%s,%s)"
                        self.db.sql(sql, (task.name, task.type, task.project, task.job, task.priority, task.n_fatals, task.n_runs))
                    else:
                        raise Exception('Unknown task type')

                elif cmd.name == 'EDIT_TASK':
                    task = params
                    if task.type=='PERIODIC':
                        job_id, = self.db.sql("select job_id from tasks where id=%s", task.id)[0]
                        if job_id:
                            self.db.sql("update jobs set status='DELETED', mtime=now() where id=%s", job_id)
                        sql = "update tasks set name=%s, project=%s, job=%s, period=%s, priority=%s, job_id=NULL " \
                              "where id=%s"
                        self.db.sql(sql, (task.name, task.project, task.job, task.period, task.priority,
                                          task.id))
                    elif task.type=='EVENT':
                        sql = "update tasks set name=%s, project=%s, job=%s, priority=%s, n_fatals=%s, n_runs=%s where id=%s"
                        self.db.sql(sql, (task.name, task.project, task.job, task.priority, task.n_fatals, task.n_runs, task.id))
                    else:
                        raise Exception('Unknown task type')

                elif cmd.name == 'DEL_JOB':
                    self.db.sql("update jobs set status='DELETED', mtime=now() where id=%s", params.job_id)

                elif cmd.name == 'RERUN_JOB':
                    self.db.sql("update jobs set status='WAIT', mtime=now() where id=%s", params.job_id)
                    self.db.sql("update scripts set status='WAIT' where job_id=%s", params.job_id)

                elif cmd.name == 'RUN_JOB_NOW':
                    self.db.sql("update jobs set run_at=NULL, mtime=now() where id=%s", params.job_id)

                elif cmd.name == 'SET_TASK_STATUS':
                    self.db.sql("update tasks set status=%s where id=%s",
                                (params.status, params.task_id))

                elif cmd.name == 'SET_HOST_STATUS':
                    self.db.sql("update values set value=%s where name='host_status'", (params.status))

                elif cmd.name == 'SET_CFG_MSG':
                    sql = "update key_values set value=%s where key='cfg_msgs'"
                    self.db.sql(sql, params.text)
                    self.msg_processor.refresh()


                else:
                    raise Exception('Unknown command')

            except Exception as err:
                raise
                print(format(err))
                error = 'Exception'

            status = 'FATAL' if error else 'DONE'
            self.db.sql("update cmds set status=%s, error=%s where id=%s", (status, error, cmd.id))

            self.periodic_init()

            if cmd.name=='SET_HOST_STATUS' and params.status=='EXIT':
                sys.exit()

    def loop(self):

        print('loop')
        t0 = 0
        while True:

            self.cmds()

            t = time.time()
            if t-t0 > 60:
                self.values['manager_mtime'] = alt.time.now_iso()
                t0 = t

            host_status = self.values['host_status']
            job_started = False
            if host_status=='RUN':

                self.resources.new_loop()

                self.inspect_running_jobs()

                if self.choose_job_to_run():
                    continue

                if self.process_events():
                    continue

            time.sleep(1)

if __name__ == '__main__':

    manager = Manager()

    manager.loop()