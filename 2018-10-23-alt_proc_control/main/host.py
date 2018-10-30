import alt_pathfrom header import *from host_jobs import Jobsfrom host_config import Configclass Host:    def __init__(self, root):        self.root = root        self.jobs = Jobs(root)    def render(self, tpl_name, **kwargs):        return self.root.render('host/' + tpl_name, **kwargs)    @cherrypy.expose    @cherrypy.tools.json_in()    def cmd(self, host):        db = cherrypy.thread_data.db.get(host)        post = dict_(cherrypy.request.json)        sql = "insert into cmds (name, params) values (%s,%s)"        db.sql(sql, (post.name, json.dumps(post.params)))        return 'OK'    @cherrypy.expose    def cmd_waiting(self, host):        db = cherrypy.thread_data.db.get(host)        n = db.sql("select count(*) as n from cmds where status='WAIT'")[0]        return str(n.n)    @cherrypy.expose    def status(self, host):        return self.render('status', host=host)    @cherrypy.expose    def status_ajax(self, host):        status = self.get_status(host)        _form = dict_(host_status=status.host_status)        for task in status.tasks:            _form['task_status_'+task.name] = task.status        html = self.render('status_ajax', host=host, _form=_form, **status)        return json.dumps(dict_(html=html, now=alt.time.now_iso()))    def get_status(self, host):        db = cherrypy.thread_data.db.get(host)        tz = 0        sql = "select value from values where name='host_status'"        host_status = db.sql(sql)[0].value        sql = "select name, value from values where name='manager_mtime'"        manager_mtime = db.sql(sql)[0].value        manager_mtime = www.time.diff_format(manager_mtime)        repl_status = None        if self.root.cfg.hub and host!=self.root.host_name:            sql = "SHOW SLAVE '%s' STATUS" % host            repl = self.root.hub_db.sql(sql)[0]            repl_ok =  repl['Slave_IO_Running']=='Yes' and repl['Slave_SQL_Running']=='Yes'            repl_status = "RUN" if repl_ok else "TODO"                    sql = """            select t.id,                 sum(case when j.status='WAIT' and j.result is null then 1 else 0 end) as wait,                 sum(case when j.status='WAIT' and j.result!='SUCCESS' and NOT j.todo then 1 else 0 end) as wait_fatal,                 sum(case when j.status='WAIT' and j.result!='SUCCESS' and j.todo then 1 else 0 end) as wait_todo,                 sum(case when j.status='RUN' and j.result is null then 1 else 0 end) as run,                 sum(case when j.status='RUN' and j.result!='SUCCESS' and NOT j.todo then 1 else 0 end) as run_fatal,                 sum(case when j.status='RUN' and j.result!='SUCCESS' and j.todo then 1 else 0 end) as run_todo,                 sum(case when j.status='DONE' and j.result='SUCCESS' and j.mtime>='{t}' then 1 else 0 end) as done,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{t}' and NOT j.todo then 1 else 0 end) as done_fatal,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{t}' and j.todo then 1 else 0 end) as done_todo,                 sum(case when j.status='DONE' and j.result='SUCCESS' and j.mtime>='{t}' and j.mtime<'{y}' then 1 else 0 end) as done_prev,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{t}' and j.mtime<'{y}' and NOT j.todo then 1 else 0 end) as done_fatal_prev,                 sum(case when j.status='DONE' and j.result!='SUCCESS' and j.mtime>='{t}' and j.mtime<'{y}' and j.todo then 1 else 0 end) as done_todo_prev             from tasks t            join events e on t.id = e.task_id            join jobs j on j.event_id=e.id            where t.type='EVENT'            GROUP BY t.id                   """        now = datetime.now()        today = datetime(year=now.year, month=now.month, day=now.day)        yesterday = today - timedelta(days=1)        today, yesterday = alt.time.iso(today), alt.time.iso(yesterday)        jobs_sql = sql.format(t=today, y=yesterday)        events_sql = """            select t.id,                 sum(case when e.status='WAIT' then 1 else 0 end) as events            from tasks t            join events e on e.task_id=t.id            where t.type='EVENT'            GROUP BY t.id                   """        errors_sql = """           select t.id,                 sum(case when m.type='ERROR' and m.active and not m.todo then 1 else 0 end) as errors,                sum(case when m.type='ERROR' and m.active and m.todo then 1 else 0 end) as errors_todo            from tasks t            join events e on e.task_id=t.id            join jobs j on j.event_id=e.id            join scripts s on s.job_id=j.id            join msgs m on m.script_id=s.id            where j.mtime>='{t}'            GROUP BY t.id                   """.format(t=today)        sql = """            select t.id, t.name, t.project, t.status, t.type,                wait, wait_fatal, wait_todo,                run, run_fatal, run_todo,                done, done_fatal, done_todo,                 done_prev, done_fatal_prev, done_todo_prev,                events,                errors, errors_todo            from tasks t             left join ({jobs}) j on j.id=t.id             left join ({events}) ev on ev.id=t.id             left join ({errors}) er on er.id=t.id         """.format(jobs=jobs_sql, events=events_sql, errors=errors_sql)        tasks = db.sql(sql)        tasks = sorted(tasks, key=lambda task: task.project)        for task in tasks:            sql = """                select j.id, j.mtime, j.stime, j.mtime, e.param, j.status, j.result                 from jobs j                join events e on j.event_id = e.id                join tasks t on e.task_id = t.id                where t.name=%s                 order by mtime desc                 limit 1                """            jobs = db.sql(sql, task.name)            if not jobs:                continue            job = jobs[0]            job.mtime_diff = www.time.diff_format(job.mtime, tz=tz)            sql = "select * from scripts where job_id=%s order by iscript"            job.scripts = db.sql(sql, job.id)            if job.stime and job.etime:                job.wtime = www.time.diff_format(job.etime, job.stime)            elif job.stime:                job.wtime = www.time.diff_format(job.stime, tz=tz)            else:                job.wtime = None            sql = """                select * from msgs                join scripts s on msgs.script_id = s.id                where job_id=%s and active                """            job.msgs = db.sql(sql, job.id)            for msg in job.msgs:                msg.stime_diff = www.time.diff_format(msg.stime, tz=tz)            task.job = job        msgs = db.sql("select * from msgs where not read")        for msg in msgs:            msg.diff = www.time.diff_format(msg.stime, msg.etime)            msg.mtime = www.time.diff_format(msg.etime, tz=tz)            msg.stime = alt.time.iso(msg.stime)[11:16]            msg.etime = alt.time.iso(msg.etime)[11:16]        return dict_(tasks=tasks, host_status=host_status, manager_mtime=manager_mtime,                     repl_status=repl_status, msgs=msgs)    @cherrypy.expose    def job(self, host, job_id):        db = cherrypy.thread_data.db.get(host)        job = db.sql("select * from jobs where id=%s", job_id)[0]        event = db.sql("select * from events where id=%s", job.event_id)[0]        task = db.sql("select * from tasks where id=%s", event.task_id)[0]        sql = """            select * from scripts s            left join runs r on s.last_run_id = r.id            where job_id=%s order by iscript        """        scripts = db.sql(sql, job.id)        return self.render('job', host=host, task=task, job=job, event=event, scripts=scripts)    def msgs(self, host, **form):        tz = self.root.host_tz(host)        default = dict_(new='new', limit=30)        form = www.form.prepare_form(form, default=default)        where = ["j.status!='DELETED'"]        if 'task' in form:            where.append("t.name='%s'" % form.task)        if form.new=='new':            where.append("m.read=0")        hub_join = ''        if self.root.hub_mode:            hub_join = "left join `alt_proc-hub`.`msgs-%s` h on m.id=h.id" % host            if form.new=='new':                where.append("(h.read=0 OR h.read is null)")        where = ' and '.join(where)        sql = """              select m.*, t.name, j.id as job_id, e.key, p.cmd               from msgs m               %s              left join jobs j on m.job_id=j.id              left join tasks t on j.task_id=t.id              left join scripts p on m.proc_id=p.id              left join events e on j.event_id=e.id              where %s               order by m.etime DESC               LIMIT %s            """ % (hub_join, where, form.limit)        msgs = db.sql(sql)        for msg in msgs:            msg.diff = www.time.diff_format(msg.stime, msg.etime)            msg.mtime = www.time.diff_format(msg.etime, tz=tz)            msg.stime = alt.time.iso(msg.stime)[11:16]            msg.etime = alt.time.iso(msg.etime)[11:16]        tasks = db.sql("select * from tasks")        msg_ids = [msg.id for msg in msgs]        return self.render(host, 'msgs', form=form, msgs=msgs, tasks=tasks, msg_ids=msg_ids)    def msg_read(self, host, msg_ids):        msg_ids = json.loads(msg_ids)        if self.root.hub_mode:            for msg_id in msg_ids:                sql = """                    insert into `msgs-%s` (id, `read`) values (%s, 1)                    on DUPLICATE KEY UPDATE `read`=1                 """ % (host, msg_id)                self.root.hub_db.sql(sql)        else:            msg_ids = str(msg_ids)[1:-1]            db.sql("UPDATE msgs SET `read`=1 where id IN (%s)" % msg_ids)        return 'OK'