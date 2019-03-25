import alt_path
from header import *

class Jobs:

    def __init__(self, root):

        self.root = root

    def render(self, tpl_name, **kwargs):

        return self.root.render('host/jobs/' + tpl_name, **kwargs)

    @cherrypy.expose
    def last(self, **form):

        return self.jobs('last', **form)

    @cherrypy.expose
    def active(self, **form):

        return self.jobs('active', **form)

    @cherrypy.expose
    def date(self, **form):

        return self.jobs('date', **form)

    @cherrypy.expose
    def param(self, **form):

        return self.jobs('param', **form)

    def jobs(self, mode, **_form):

        db = cherrypy.thread_data.db
        default = dict_(_limit=30)
        _form = www.form.prepare_form(_form, default)

        sort, where, params = 'ASC', ["j.status!='DELETED'", "t.status!='DELETED'"], []
        if mode=='last':
            sort = 'DESC'

        if mode=='active':
            where.append("j.status in ('WAIT','RUN')")

        if 'task' in _form:
            if _form.task=='_periodic':
                where.append("t.type='PERIODIC'")
            else:
                where.append("t.name='%s'" % _form.task)
        if 'result' in _form:
            where.append("j.status='DONE' and j.result=%s")
            params += [_form.result.upper()]
        if 'date' in _form:
            where.append("j.mtime >= %s and j.mtime < %s")
            dt0 = alt.time.from_iso(_form.date)
            dt1 = dt0 + timedelta(days=1)
            params += [dt0, dt1]
        if 'param' in _form:
            where.append("e.param=%s")
            params += [_form.param]

        where = ' and '.join(where)

        sql = """
            select j.job_id, j.status, j.result, j.mtime, j.stime, j.etime, 
                t.name as task, t.type, e.param 
            from jobs j
            join events e on j.event_id = e.event_id
            join tasks t on e.task_id = t.task_id
            where %s
            order by j.mtime %s 
            limit %s
        """ % (where, sort, _form._limit)
        print(sql)
        jobs = db.sql(sql, params)

        for job in jobs:
            if mode=='date':
                job.mtime = alt.time.iso(job.mtime)[11:16]
            elif mode=='param':
                job.mtime = alt.time.iso(job.mtime)[:-3]
            else:
                job.mtime = www.time.diff_format(job.mtime)
            if job.stime and job.etime:
                job.wtime = www.time.diff_format(job.etime, job.stime)
            job.scripts = db.sql("select * from scripts where job_id=%s order by iscript", job.job_id)
            sql = """
                select * from msgs m
                join scripts s on m.script_id = s.script_id
                join jobs j on s.job_id = j.job_id
                where j.job_id=%s and m.active
            """
            job.msgs = db.sql(sql, job.job_id)
            for msg in job.msgs:
                msg.stime_diff = www.time.diff_format(msg.stime)

        sql = "select name from tasks where type!='PERIODIC' and status!='DELETED'"
        tasks = db.sql(sql)
        job_ids = []
        for job in jobs:
            job_ids.append(job.job_id)

        _form._default = default

        return self.render(mode, _form=_form, jobs=jobs, tasks=tasks,
                           today=alt.time.today(), job_ids=job_ids)

