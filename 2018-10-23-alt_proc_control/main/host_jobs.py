import alt_path
from header import *

class Jobs:

    def __init__(self, root):

        self.root = root

    def render(self, tpl_name, **kwargs):

        return self.root.render('host/jobs/' + tpl_name, **kwargs)

    @cherrypy.expose
    def last(self, host, **form):

        return self.jobs('last', host=host, **form)

    def active(self, host, **form):

        return self.jobs(host, 'active', **form)

    def date(self, host, **form):

        return self.jobs(host, 'date', **form)

    def key(self, host, **form):

        return self.jobs(host, 'key', **form)

    def jobs(self, mode, host, **_form):

        db = cherrypy.thread_data.db.get(host)
        default = dict_(limit=30)
        _form = www.form.prepare_form(_form, default)
        limit = _form.get('limit', default)

        sort, where = 'ASC', ['1=1']
        if mode=='last':
            sort = 'DESC'

        if 'task' in _form:
            if _form.task=='_periodic':
                where.append("t.type='PERIODIC'")
            else:
                where.append("t.name='%s'" % _form.task)

        where = ' and '.join(where)

        sql = """
            select j.id, t.name as task, e.param, j.status, j.result, j.mtime, j.stime, j.etime
            from jobs j
            join events e on j.event_id = e.id
            join tasks t on e.task_id = t.id
            where %s
            order by j.mtime %s 
            limit %s
        """ % (where, sort, _form.limit)
        print(sql)
        jobs = db.sql(sql)

        for job in jobs:
            job.mtime = www.time.diff_format(job.mtime)
            if job.stime and job.etime:
                job.wtime = www.time.diff_format(job.etime, job.stime)
            job.scripts = db.sql("select * from scripts where job_id=%s order by id", job.id)
            sql = """
                select * from msgs
                join scripts s2 on msgs.script_id = s2.id
                join jobs j on s2.job_id = j.id
                where job_id=%s and msgs.active
            """
            job.msgs = db.sql(sql, job.id)
            for msg in job.msgs:
                msg.stime_diff = www.time.diff_format(msg.stime)

        sql = "select name from tasks where type!='PERIODIC'"
        tasks = db.sql(sql)

        _form._default = default

        return self.render('last', host=host, _form=_form, jobs=jobs, tasks=tasks)

    # @cherrypy.expose
    # def jobs(self, host, mode, **form):
    #
    #     default = dict_(mode='last', limit=30)
    #     form = www.form.prepare_form(form, default)
    #     tz = self.root.host_tz(host)
    #
    #     sort, where = 'ASC', []
    #     if mode=='last':
    #         sort = 'DESC'
    #
    #     if 'task' in form:
    #         if form.task=='_periodic':
    #             where.append("tasks.type='PERIODIC'")
    #         else:
    #             where.append("tasks.name='%s'" % form.task)
    #     if form.get('result')=='fatal':
    #             where.append("result IN ('FATAL','ERRORS')")
    #     if mode=='active':
    #         where.append("jobs.status IN ('RUN','WAIT')")
    #     if mode=='date':
    #         if not 'date' in form:
    #             form.date = alt.time.iso(datetime.today().date())
    #         time0 = datetime.strptime(form.date, '%Y-%m-%d') + timedelta(hours=tz)
    #         time1 = time0 + timedelta(days=1)
    #         where.append("jobs.mtime>='%s' and jobs.mtime<'%s'" %
    #                      ( alt.time.iso(time0),alt.time.iso(time1)))
    #     if mode=='key':
    #         where.append("events.key='%s'" % form.get('key','None'))
    #
    #     if where:
    #         where = 'and ' + ' and '.join(where)
    #     else:
    #         where = ''
    #     sql = '''
    #         select jobs.id from jobs
    #         left join tasks on jobs.task_id=tasks.id
    #         left join events on jobs.event_id=events.id
    #         where jobs.status!='DELETED' %s
    #         order by mtime %s LIMIT %s
    #     ''' % (where, sort, form.limit)
    #     job_ids = db.sql(sql)
    #
    #     jobs = []
    #     for job_id in job_ids:
    #         job_id = job_id.id
    #         sql = """
    #             select j.*, t.name as task, t.type as task_type, e.key
    #             from jobs j
    #             left join tasks t on j.task_id=t.id
    #             left join events e on j.event_id=e.id
    #             where j.id=%s
    #             """
    #         job = db.sql(sql, job_id)[0]
    #         if mode in ('last','active'):
    #             job.mtime = www.time.diff_format(job.mtime, tz=tz)
    #         elif mode == 'form.date':
    #             job.mtime = alt.time.iso(job.mtime - timedelta(hours=tz))[11:-3]
    #         elif mode=='form.key':
    #             job.mtime = alt.time.iso(job.mtime - timedelta(hours=tz))
    #         job.scripts = db.sql("select * from scripts where job_id=%s order by id", job_id)
    #         sql = "select * from msgs where job_id=%s and msgs.active"
    #         job.msgs = db.sql(sql, job_id)
    #         for msg in job.msgs:
    #             msg.stime_diff = www.time.diff_format(msg.stime, tz=tz)
    #         if job.stime and job.etime:
    #             job.wtime = www.time.diff_format(job.etime, job.stime)
    #         elif job.stime:
    #             job.wtime = www.time.diff_format(job.stime, tz=tz)
    #         else:
    #             job.wtime = None
    #         jobs.append(job)
    #
    #     tasks = db.sql("select name from tasks where tasks.type!='PERIODIC' order by name")
    #
    #     return self.render(host, mode, tasks=tasks, jobs=jobs, form=form,
    #                        default=default)
