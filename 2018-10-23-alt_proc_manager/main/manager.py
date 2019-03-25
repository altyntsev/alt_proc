import alt_path
from _header import *
import db_lib

class Msg_processor:

    def __init__(self, root):

        self.root = root
        self.reload()

    def reload(self):

        text = self.root.values['cfg_msgs']
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

    def run_done(self, job):

        sql = """
            select m.msg_id, m.script_id, m.msg, m.type, m.n_runs 
            from msgs m
            join scripts s on m.script_id = s.script_id
            where s.job_id=%s AND active
            """
        existing_msgs = self.root.db.sql(sql, job.job_id)
        todo = False

        job.msgs = [dict_(msg) for msg in json.loads(job.msgs)] if job.msgs else []

        obsolete_msg_ids = [msg.msg_id for msg in existing_msgs]
        for msg in job.msgs:
            for existing_msg in existing_msgs:
                if existing_msg.script_id==job.script_id and existing_msg.msg==msg.msg: # same msg
                    todo = self.todo(existing_msg, job, job, job, job)
                    print(msg.msg, todo)
                    existing_msg.etime = job.etime
                    existing_msg.n_runs += 1
                    sql = "update msgs set etime = %s, n_runs = %s, todo = %s where msg_id=%s"
                    self.root.db.sql(sql, (existing_msg.etime, existing_msg.n_runs, todo,
                                           existing_msg.msg_id))
                    obsolete_msg_ids.remove(existing_msg.msg_id)
                    break
            else: # new msg
                todo = self.todo(msg, job, job, job, job)
                sql = """
                    insert into msgs 
                    (msg, type, script_id, stime, etime, todo)
                    values (%s,%s,%s,%s,%s,%s)                    """
                self.root.db.sql(sql, (msg.msg, msg.type, job.script_id,
                                       job.stime, job.stime, todo))

        # obsolete
        for msg_id in obsolete_msg_ids:
            self.root.db.sql("update msgs set active=false, todo=%s where msg_id=%s", (todo, msg_id))

        return todo

class Resources:

    def __init__(self, manager):

        self.manager = manager
        self.reload()

    def reload(self):

        self.resources = dict_(json.loads(self.manager.values['cfg_resources']))

    def new_loop(self):

        self.loop_resources = dict_(self.resources)

    def use(self, resources):

        if resources:
            for name, value in resources.items():
                self.loop_resources[name] -= value

    def available(self, resources):

        if resources:
            for name, value in resources.items():
                if self.loop_resources[name]<value:
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
        self.values = db_lib.Values(self.db)
        self.msg_processor = Msg_processor(self)

        tasks = self.db.sql("select * from tasks")
        self.n_fatals = {}
        for task in tasks:
            self.n_fatals[task.task_id] = dict_(value=task.n_fatals, current=task.n_fatals)

        host_status = self.values['host_status']

        if host_status=='EXIT':
            self.values['host_status'] = 'RUN'

        self.resources = Resources(self)
        self.cmds()

        print(alt.time.now(), ': ALT_Processing manager started')

    def process_events(self):

        sql = """
            select e.event_id, t.name as task 
            from tasks t 
            left join events e on t.task_id = e.task_id
            left join (
                select t.task_id, t.n_runs, count(j.job_id) as n_used
                from tasks t
                left join events e on t.task_id = e.task_id
                left join jobs j on e.event_id = j.event_id
                where j.status in ('RUN', 'WAIT')
                group by t.task_id, t.n_runs) sel on sel.task_id=t.task_id           
            where t.status='ACTIVE' and e.status='WAIT' and 
                (sel.n_used is null or sel.n_used<sel.n_runs)
            order by priority
            """
        events = self.db.sql(sql)
        for event in events:
            self.create_job(event.event_id)
            sql = "update events set status='USED' where event_id=%s"
            self.db.sql(sql, event.event_id)
            return True
        return False

    def create_job(self, event_id):

        sql = """
            select t.name, t.project from tasks t
            left join events e on e.task_id=t.task_id
            where e.event_id=%s
            """
        task, = self.db.sql(sql, event_id)
        task_file = '%s/projects/%s/main/_cfg/%s.task' % \
                (self.root_dir, task.project, task.name)
        task_cfg = alt.cfg.read(task_file)
        if 'scripts' not in task_cfg:
            raise Exception('No scripts in task cfg file')
        sql = "insert into jobs (event_id, mtime) values (%s, now())"
        job_id = self.db.sql(sql, event_id, return_id='job_id')
        job_wd = self.alt_proc_wd + 'jobs/%s/' % job_id
        task_resources = task_cfg.get('resources',{})
        for iscript, script in enumerate(task_cfg.scripts):
            sql = "insert into scripts (job_id, iscript, cmd, name, resources) " \
                  "values (%s,%s,%s,%s,%s)"
            resources = dict(task_resources)
            script_cmd = '%s/projects/%s/main/%s' % \
                       (self.root_dir, task.project, script.cmd)
            script_cmd = alt.file.abspath(script_cmd)
            with open(script_cmd) as f:
                first_line = f.readline()
            if '# resources:' in first_line:
                script_resources = dict_(yaml.load(first_line[1:])).resources
                resources.update(script_resources)
            script_resources = script.get('resources',{})
            resources.update(script_resources)
            self.db.sql(sql, (job_id, iscript, script.cmd, alt.file.name(script.cmd),
                              json.dumps(resources)))
            script_wd = job_wd + '_{0:02d}/'.format(iscript)
            alt.file.mkdir(script_wd)
            alt.file.write(script_wd + 'run.cfg', script_cmd)
            alt.file.write(script_wd + 'run.bash', 'ipython /alt_proc/projects/_cfg/run.py')
            if os.name=='posix':
                alt.system.run('chmod u+x ' + script_wd + 'run.bash')

    def inspect_running_jobs(self):

        sql = """
            select t.name as task, t.type, t.period, t.project, t.task_id,
                j.job_id, s.script_id, s.cmd, s.resources,
                r.result, r.restart_after, r.msgs, r.stime, r.etime
            from jobs j
            join events e on j.event_id = e.event_id
            join tasks t on e.task_id = t.task_id
            join scripts s on j.job_id = s.job_id
            left join runs r on s.last_run_id=r.run_id
            where j.status='RUN' and s.status='RUN' and t.status!='DEBUG'
        """
        jobs = self.db.sql(sql)
        for job in jobs:

            if job.result is None: # script is working
                self.resources.use(job.resources)
                continue

            print(alt.time.now(), ': Script', job.project, ':', job.cmd, 'finished')
            self.msg_processor.run_done(job)

            if job.restart_after: # restart
                sql = "update scripts set status = 'WAIT', result = %s where script_id=%s"
                self.db.sql(sql, (job.result, job.script_id))
                sql = """
                    update jobs 
                    set status='WAIT', run_at=now() + INTERVAL '%s minute', result = %s, 
                        mtime=now() 
                    where job_id=%s
                    """
                self.db.sql(sql, (job.restart_after, job.result, job.job_id))
                continue

            # script done
            sql = "update scripts set status='DONE', result = %s where script_id=%s"
            self.db.sql(sql, (job.result, job.script_id))
            sql = "update jobs set status='WAIT', mtime=now() where job_id=%s"
            self.db.sql(sql, job.job_id)

            # job done?
            sql = """
                select s.status, s.result
                from scripts s 
                join jobs j on s.job_id = j.job_id
                where j.job_id=%s
                order by s.iscript
            """
            scripts = self.db.sql(sql, (job.job_id))
            job_status, job_result = 'DONE', 'SUCCESS'
            for script in scripts:
                if script.status!='DONE':
                    job_status = script.status
                    break
                if script.result=='FATAL':
                    job_result = 'FATAL'
                    job_status = 'DONE'
                    break
                if job_result=='SUCCESS' and script.result=='ERRORS':
                    job_result = 'ERRORS'
            if job_status!='DONE':
                continue

            # job done!
            if job.type=='PERIODIC':
                sql = """
                    update jobs 
                    set status='WAIT', run_at=now() + INTERVAL '%s minute', result = %s, mtime=now(), 
                        etime=now() 
                    where job_id=%s
                    """
                self.db.sql(sql, (job.period, job_result, job.job_id))
                sql = """
                    update scripts
                    set status='WAIT' 
                    from scripts s
                    join jobs j on s.job_id=j.job_id
                    where scripts.script_id=s.script_id and j.job_id=%s 
                """
                self.db.sql(sql, (job.job_id))
            else:
                sql = """
                    update jobs set status='DONE', result=%s, mtime=now(), etime=now() 
                    where job_id=%s
                    """
                self.db.sql(sql, (job_result, job.job_id))

            # check n_fatals
            if job_result=='FATAL':
                self.n_fatals[job.task_id].current -= 1
                if self.n_fatals[job.task_id].value!=0 and self.n_fatals[job.task_id].current<=0:
                    self.db.sql("update tasks set status='TODO' where task_id=%s", job.task_id)
            else:
                self.n_fatals[job.task_id].current = self.n_fatals[job.task_id].value

    def choose_job_to_run(self):

        sql = """
            select j.job_id, t.name as task 
            from jobs j 
            left join events e on j.event_id = e.event_id
            left join tasks t on e.task_id = t.task_id
            left join (
                select t.task_id, t.n_runs, count(j.job_id) as n_used
                from tasks t
                left join events e on t.task_id = e.task_id
                left join jobs j on e.event_id = j.event_id
                where j.status='RUN'
                group by t.task_id, t.n_runs) sel on sel.task_id=t.task_id           
            where t.status='ACTIVE' and j.status='WAIT' and 
                (j.run_at is null or j.run_at<now()) and 
                (sel.n_used is null or sel.n_used<sel.n_runs) 
            order by t.priority desc, j.ctime asc, job_id asc 
            """
        jobs = self.db.sql(sql)

        for job in jobs:
            sql = """
                select s.script_id, s.iscript, s.cmd, t.project, s.resources
                from scripts s 
                join jobs j on s.job_id = j.job_id
                join events e on j.event_id = e.event_id
                join tasks t on e.task_id = t.task_id
                where j.job_id=%s and s.status='WAIT'
                order by s.iscript
                limit 1
            """
            script = self.db.sql(sql, job.job_id, return_one=True)

            if not self.resources.available(script.resources):
                continue

            self.start_script(script.script_id)
            return True

        return False

    def start_script(self, script_id):

        sql = """
            select s.script_id, s.iscript, s.cmd, t.project, j.job_id
            from scripts s 
            join jobs j on s.job_id = j.job_id
            join events e on j.event_id = e.event_id
            join tasks t on e.task_id = t.task_id
            where s.script_id=%s
        """
        script = self.db.sql(sql, script_id, return_one=True)
        job_id = script.job_id

        job_wd = self.alt_proc_wd + 'jobs/%s/' % job_id
        script_wd = job_wd + '_{0:02d}/'.format(script.iscript)
        alt.file.mkdir(script_wd)
        script_cmd = '%s/projects/%s/main/%s' % \
                   (self.root_dir, script.project, script.cmd)
        script_cmd = alt.file.abspath(script_cmd)
        alt.file.write(script_wd + 'run.cfg', script_cmd)
        alt.file.write(script_wd + 'run.bash', 'ipython /alt_proc/projects/_cfg/run.py')
        if os.name=='posix':
            alt.system.run('chmod u+x ' + script_wd + 'run.bash')

        cmd = '%s %s >>log.txt 2>&1' % (sys.executable, script_cmd)
        print(alt.time.now(), ': Script', script.project, ':', script.cmd, 'started')
        os_pid = subprocess.Popen(cmd, cwd=script_wd, shell=True).pid

        sql = "update jobs set status='RUN', os_pid=%s, mtime=now() where job_id=%s"
        self.db.sql(sql, (os_pid, job_id))
        if script.iscript==0:
            sql = "update jobs set stime=now(), etime=null where job_id=%s"
            self.db.sql(sql, job_id)

        sql = """
            update scripts
            set status='RUN', last_run_id=null 
            from scripts s
            join jobs j on s.job_id=j.job_id
            where scripts.script_id=s.script_id and j.job_id=%s and s.iscript=%s
        """
        self.db.sql(sql, (job_id, script.iscript))

    def cmds(self):

        for cmd in self.db.sql("select * from cmds where status='WAIT'"):
            print('CMD = ', cmd.name, cmd.params)

            error = None
            params = cmd.params
            try:

                if cmd.name == 'NEW_TASK':
                    task = params
                    sql = "select * from tasks where name=%s and status!='DELETED'"
                    if self.db.sql(sql, task.name):
                        raise Exception('Task name exists')
                    if task.type=='PERIODIC':
                        sql = """
                            insert into tasks 
                            (name, type, project, period, priority) 
                            values (%s,%s,%s,%s,%s)
                            """
                        task_id = self.db.sql(sql, (task.name, task.type, task.project,
                            task.period, task.priority), return_id='task_id')
                        sql = "insert into events (task_id) values (%s)"
                        self.db.sql(sql, task_id)
                    elif task.type=='EVENT':
                        sql = """
                            insert into tasks 
                            (name, type, project, priority, n_fatals, n_runs) 
                            values (%s,%s,%s,%s,%s,%s)
                            """
                        task_id = self.db.sql(sql, (task.name, task.type, task.project,
                            task.priority, task.n_fatals, task.n_runs), return_id='task_id')
                    else:
                        raise Exception('Unknown task type')
                    self.n_fatals[task_id] = dict_(value=task.n_fatals, current=task.n_fatals)

                elif cmd.name == 'EDIT_TASK':
                    task = params
                    if task.type=='PERIODIC':
                        sql = """
                            update tasks 
                            set name = %s, project = %s, period = %s, priority = %s, n_fatals = %s 
                            where task_id=%s
                            """
                        self.db.sql(sql, (task.name, task.project, task.period, task.priority,
                                          task.n_fatals, task.task_id))
                        sql = """
                            update jobs
                            set status='DELETED'
                            from jobs j
                            left join events e on j.event_id = e.event_id
                            left join tasks t on e.task_id = t.task_id
                            where jobs.job_id=j.job_id and t.task_id=%s
                            """
                        self.db.sql(sql, task.task_id)
                        sql = "update events set status='WAIT' where task_id=%s"
                        self.db.sql(sql, task.task_id)
                    elif task.type=='EVENT':
                        sql = """
                            update tasks 
                            set name = %s, project = %s, priority = %s, n_fatals = %s, n_runs = %s 
                            where task_id = %s
                            """
                        self.db.sql(sql, (task.name, task.project, task.priority, task.n_fatals, task.n_runs,
                                          task.task_id))
                    else:
                        raise Exception('Unknown task type')
                    self.n_fatals[task.task_id] = dict_(value=task.n_fatals, current=task.n_fatals)

                elif cmd.name == 'SET_TASK_STATUS':
                    task = params
                    self.db.sql("update tasks set status = %s where task_id = %s",
                                (task.status, task.task_id))
                    if task.status=='ACTIVE':
                        self.n_fatals[task.task_id].current = self.n_fatals[task.task_id].value

                elif cmd.name == 'DEL_JOB':
                    self.db.sql("update jobs set status='DELETED', mtime=now() where job_id=%s", params.job_id)

                elif cmd.name == 'DEL_AND REEMIT':
                    self.db.sql("update jobs set status='DELETED', mtime=now() where job_id=%s", params.job_id)
                    event = self.db.sql("select event_id from jobs where job_id=%s", params.job_id,
                                           return_one=True)
                    self.db.sql("update events set status='WAIT' where event_id=%s", event.event_id)

                elif cmd.name == 'RERUN_JOB':
                    self.db.sql("update scripts set status='WAIT' where job_id=%s", params.job_id)
                    self.db.sql("update jobs set status='WAIT', mtime=now() where job_id=%s", params.job_id)

                elif cmd.name == 'RERUN_JOBS':
                    for job_id in params.job_ids:
                        wd = self.alt_proc_wd + 'jobs/%s/' % job_id
                        if os.path.exists(wd):
                            self.db.sql("""update scripts set status='WAIT' 
                                           where job_id=%s and status='DONE' and result!='SUCCESS'
                                        """, job_id)
                        else:
                            self.db.sql("update scripts set status='WAIT' where job_id=%s", job_id)
                        self.db.sql("update jobs set status='WAIT', mtime=now() where job_id=%s", job_id)

                elif cmd.name == 'RUN_JOB_NOW':
                    self.db.sql("update jobs set run_at=NULL, mtime=now() where job_id=%s", params.job_id)

                elif cmd.name == 'RERUN_SCRIPT':
                    script = self.db.sql("select job_id from scripts where script_id=%s", params.script_id,
                                           return_one=True)
                    self.db.sql("""
                        update scripts set status='WAIT' where job_id=%s and script_id>=%s""",
                        (script.job_id, params.script_id))
                    self.db.sql("update jobs set status='WAIT', mtime=now() where job_id=%s", script.job_id)

                elif cmd.name == 'SET_HOST_STATUS':
                    self.db.sql("update values set value=%s where name='host_status'", (params.status))

                elif cmd.name == 'SET_CFG_MSG':
                    sql = "update key_values set value=%s where key='cfg_msgs'"
                    self.db.sql(sql, params.text)
                    self.msg_processor.reload()

                elif cmd.name == 'SET_HOST_RESOURCES':
                    sql = "update values set value=%s where name='cfg_resources'"
                    print(params)
                    self.db.sql(sql, params.text)
                    self.resources.reload()

                else:
                    raise Exception('Unknown command')

            except Exception as err:
                raise
                print(format(err))
                error = 'Exception'

            status = 'FATAL' if error else 'DONE'
            self.db.sql("update cmds set status=%s, error=%s where cmd_id=%s", (status, error, cmd.cmd_id))
            self.resources.reload()

            if cmd.name=='SET_HOST_STATUS' and params.status=='EXIT':
                sys.exit()

    def loop(self):

        print('loop')
        t0 = 0
        while True:

            self.cmds()

            t = time.time()
            if t-t0 > 60:
                self.values['manager_mtime'] = alt.time.now()
                t0 = t

            host_status = self.values['host_status']
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