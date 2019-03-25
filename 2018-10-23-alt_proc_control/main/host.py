import alt_pathfrom header import *from host_jobs import Jobsfrom host_config import Host_configclass Host:    def __init__(self, root):        self.root = root        self.jobs = Jobs(root)        self.config = Host_config(root)    def render(self, tpl_name, **kwargs):        return self.root.render('host/' + tpl_name, **kwargs)    @cherrypy.expose    @cherrypy.tools.json_in()    def cmd(self):        self.root.auth('admin')        post = dict_(cherrypy.request.json)        self.cmd_save(post.name, post.params)        return 'OK'    def cmd_save(self, name, params):        self.root.auth('admin')        db = cherrypy.thread_data.db        sql = "insert into cmds (name, params) values (%s,%s)"        db.sql(sql, (name, json.dumps(params)))    @cherrypy.expose    def cmd_waiting(self):        db = cherrypy.thread_data.db        n = db.sql("select count(*) as n from cmds where status='WAIT'")[0]        return str(n.n)    @cherrypy.expose    def status(self):        return self.render('status')    @cherrypy.expose    def status_ajax(self):        status = self.get_status()        _form = dict_(host_status=status.host_status)        for task in status.tasks:            _form['task_status_'+task.name] = task.status        html = self.render('status_ajax', _form=_form, **status)        return json.dumps(dict_(html=html, now=alt.time.now()))    def get_status(self):        db = cherrypy.thread_data.db        tz = 0        sql = "select value from values where name='host_status'"        host_status = db.sql(sql)[0].value        sql = "select name, value from values where name='manager_mtime'"        manager_mtime = db.sql(sql)[0].value        manager_mtime = www.time.diff_format(manager_mtime)        sql = """            select t.task_id,                 sum(case when j.status='WAIT' and j.result is null then 1 else 0 end) as wait,                 sum(case when j.status='WAIT' and j.result!='SUCCESS' and NOT j.todo then 1 else 0 end) as wait_fatal,                 sum(case when j.status='WAIT' and j.result!='SUCCESS' and j.todo then 1 else 0 end) as wait_todo,                 sum(case when j.status='RUN' and j.result is null then 1 else 0 end) as run,                 sum(case when j.status='RUN' and j.result!='SUCCESS' and NOT j.todo then 1 else 0 end) as run_fatal,                 sum(case when j.status='RUN' and j.result!='SUCCESS' and j.todo then 1 else 0 end) as run_todo,                 sum(case when j.status='DONE' and j.result='SUCCESS' and j.mtime>='{t}' then 1 else 0 end) as done,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{t}' and NOT j.todo then 1 else 0 end) as done_fatal,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{t}' and j.todo then 1 else 0 end) as done_todo,                 sum(case when j.status='DONE' and j.result='SUCCESS' and j.mtime>='{y}' and j.mtime<'{t}' then 1 else 0 end) as done_prev,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{y}' and j.mtime<'{t}' and NOT j.todo then 1 else 0 end) as done_fatal_prev,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{y}' and j.mtime<'{t}' and j.todo then 1 else 0 end) as done_todo_prev             from tasks t            join events e on t.task_id = e.task_id            join jobs j on j.event_id=e.event_id            where t.type='EVENT'            GROUP BY t.task_id                   """        now = datetime.now()        today = datetime(year=now.year, month=now.month, day=now.day)        yesterday = today - timedelta(days=1)        today, yesterday = alt.time.iso(today), alt.time.iso(yesterday)        jobs_sql = sql.format(t=today, y=yesterday)        events_sql = """            select t.task_id,                 sum(case when e.status='WAIT' then 1 else 0 end) as events            from tasks t            join events e on e.task_id=t.task_id            where t.type='EVENT'            GROUP BY t.task_id                   """        errors_sql = """           select t.task_id,                 sum(case when m.type='ERROR' and m.active and not m.todo then 1 else 0 end) as errors,                sum(case when m.type='ERROR' and m.active and m.todo then 1 else 0 end) as errors_todo            from tasks t            join events e on e.task_id=t.task_id            join jobs j on j.event_id=e.event_id            join scripts s on s.job_id=j.job_id            join msgs m on m.script_id=s.script_id            where j.mtime>='{t}'            GROUP BY t.task_id                   """.format(t=today)        sql = """            select t.task_id, t.name, t.project, t.status, t.type,                wait, wait_fatal, wait_todo,                run, run_fatal, run_todo,                done, done_fatal, done_todo,                 done_prev, done_fatal_prev, done_todo_prev,                events,                errors, errors_todo            from tasks t             left join ({jobs}) j on j.task_id=t.task_id             left join ({events}) ev on ev.task_id=t.task_id             left join ({errors}) er on er.task_id=t.task_id             where t.status!='DELETED'            order by t.project, t.name        """.format(jobs=jobs_sql, events=events_sql, errors=errors_sql)        tasks = db.sql(sql)        tasks = sorted(tasks, key=lambda task: task.project)        for task in tasks:            sql = """                select j.job_id, j.mtime, j.stime, j.mtime, j.etime, j.status, j.result,                     e.param                  from jobs j                join events e on j.event_id = e.event_id                join tasks t on e.task_id = t.task_id                where t.name=%s                 order by mtime desc                 limit 1                """            jobs = db.sql(sql, task.name)            if not jobs:                continue            job = jobs[0]            job.mtime_diff = www.time.diff_format(job.mtime, tz=tz)            sql = "select * from scripts where job_id=%s order by iscript"            job.scripts = db.sql(sql, job.job_id)            if job.stime and job.etime:                job.wtime = www.time.diff_format(job.etime, job.stime)            elif job.stime:                job.wtime = www.time.diff_format(job.stime, tz=tz)            else:                job.wtime = None            sql = """                select * from msgs                join scripts s on msgs.script_id = s.script_id                where job_id=%s and active                """            job.msgs = db.sql(sql, job.job_id)            for msg in job.msgs:                msg.stime_diff = www.time.diff_format(msg.stime, tz=tz)            task.job = job        msgs = db.sql("select * from msgs where not read")        for msg in msgs:            msg.diff = www.time.diff_format(msg.stime, msg.etime)            msg.mtime = www.time.diff_format(msg.etime, tz=tz)            msg.stime = alt.time.iso(msg.stime)[11:16]            msg.etime = alt.time.iso(msg.etime)[11:16]        return dict_(tasks=tasks, host_status=host_status, manager_mtime=manager_mtime,                     msgs=msgs)    @cherrypy.expose    def job(self, job_id):        db = cherrypy.thread_data.db        job = db.sql("select * from jobs where job_id=%s", job_id)[0]        job.ctime_diff = www.time.diff_format(job.ctime)        job.ctime = alt.time.iso(job.ctime)        job.mtime_diff = www.time.diff_format(job.mtime)        job.mtime = alt.time.iso(job.mtime)        job.stime_diff = www.time.diff_format(job.stime)        job.etime_diff = www.time.diff_format(job.etime)        job.wtime = www.time.diff_format(job.stime, job.etime)        if job.run_at:            job.run_at_diff = www.time.diff_format(job.run_at)            job.run_at = alt.time.iso(job.run_at)        event = db.sql("select * from events where event_id=%s", job.event_id)[0]        task = db.sql("select * from tasks where task_id=%s", event.task_id)[0]        sql = """            select *, s.script_id from scripts s            left join runs r on s.last_run_id = r.run_id            where job_id=%s             order by iscript        """        scripts = db.sql(sql, job.job_id)        for script in scripts:            script.stime_diff = www.time.diff_format(script.stime)            script.etime_diff = www.time.diff_format(script.etime)            script.wtime = www.time.diff_format(script.stime, script.etime)        return self.render('job', task=task, job=job, event=event, scripts=scripts)    @cherrypy.expose    def msgs(self, **_form):        tz = 0        default = dict_(new='new', limit=30)        _form = www.form.prepare_form(_form, default=default)        db = cherrypy.thread_data.db        where = ["j.status!='DELETED'"]        if 'task' in _form:            where.append("t.name='%s'" % _form.task)        if _form.new== 'new':            where.append("m.read=false")        where = ' and '.join(where)        sql = """              select m.*, t.name, j.job_id, e.param, s.cmd               from msgs m               left join scripts s on m.script_id=s.script_id              left join jobs j on s.job_id=j.job_id              left join events e on j.event_id = e.event_id              left join tasks t on e.task_id = t.task_id              where %s               order by m.etime DESC               limit %s            """ % (where, _form.limit)        msgs = db.sql(sql)        for msg in msgs:            msg.diff = www.time.diff_format(msg.stime, msg.etime)            msg.mtime = www.time.diff_format(msg.etime, tz=tz)            msg.stime = alt.time.iso(msg.stime)[11:16]            msg.etime = alt.time.iso(msg.etime)[11:16]        tasks = db.sql("select * from tasks")        msg_ids = [msg.msg_id for msg in msgs]        return self.render('msgs', _form=_form, msgs=msgs, tasks=tasks, msg_ids=msg_ids)    @cherrypy.tools.json_in()    @cherrypy.expose    def msg_read(self):        db = cherrypy.thread_data.db        post = dict_(cherrypy.request.json)        db.sql("update msgs set read=true where msg_id in %s", (tuple(post.msg_ids),))        return 'OK'