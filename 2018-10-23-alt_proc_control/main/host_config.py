import alt_path
from header import *

class Host_config:

    def __init__(self, root):

        self.root = root

        self.task = Task(root)
        self.msgs = Msgs(root)
        self.resources = Resources(root)

class Task:

    def __init__(self, root):

        self.root = root

    @cherrypy.expose
    def list(self):

        db = cherrypy.thread_data.db
        tasks = db.sql("select * from tasks t where t.status!='DELETED' order by t.project, t.name")

        return self.root.render('host/config/task/list', tasks=tasks)

    @cherrypy.expose
    def edit(self, task_id, _form=None, type=None):

        db = cherrypy.thread_data.db
        error = None

        if cherrypy.request.method=='POST':
            self.root.auth('admin')
            _form = www.form.prepare_form(_form)
            if task_id=='new':
                if db.sql("select * from tasks where name=%s and status!='DELETED'", _form.name):
                    error = 'Task name exists'
            if not _form.name:
                error = 'Empty name'
            if not _form.project:
                error = 'Empty project'
            if not error:
                task = dict_(
                    type = _form.type.upper(),
                    name = _form.name,
                    project = _form.project,
                    priority = int(_form.priority),
                    n_fatals = int(_form.n_fatals)
                )
                if task.type=='PERIODIC':
                    task.period = int(_form.period)
                if task.type=='EVENT':
                    task.n_runs = int(_form.n_runs)
                if task_id=='new':
                    cmd = 'NEW_TASK'
                else:
                    cmd = 'EDIT_TASK'
                    task.task_id = task_id
                self.root.host.cmd_save(cmd, task)
                url = self.root.cfg.root_url + '/host/config/task/list/'
                raise cherrypy.HTTPRedirect(url)

        if cherrypy.request.method=='GET' or error:
            if task_id!='new':
                task = db.sql("select * from tasks where task_id=%s", task_id)[0]
            else:
                task = dict_(type=type)
            if not error:
                _form = task
            return self.root.render('host/config/task/edit_' + task.type.lower(), _form=_form,
                                    error=error, task_id=task_id, task=task, type=type)

class Msgs:

    def __init__(self, root):

        self.root = root

    @cherrypy.expose
    def edit(self, _form=None):

        db = cherrypy.thread_data.db
        error = None
        if cherrypy.request.method=='POST':
            self.root.auth('admin')
            _form = www.form.prepare_form(_form)
            for i, line in enumerate(_form.text.split('\n')):
                if not line.strip():
                    continue
                m = re.match('([+-] *(.+?) *(.+?) *\"(.+?)\" *(.*))', line)
                if not m:
                    error = 'Wrong format in line %s' % (i+1)
            if not error:
                self.root.host.cmd('SET_CFG_MSG', dict_(text=_form.text))
                raise cherrypy.HTTPRedirect('/config/msgs/')

        if cherrypy.request.method=='GET' or error:
            if not error:
                sql = "select value from values where name='cfg_msgs'"
                text = db.sql(sql)[0].value
                _form = dict_(text=text)
            return self.root.render('/host/config/msgs/edit', _form=_form,
                                    error=error)

class Resources:

    def __init__(self, root):

        self.root = root

    @cherrypy.expose
    def edit(self, _form=None):

        db = cherrypy.thread_data.db
        error = None
        if cherrypy.request.method=='POST':
            self.root.auth('admin')
            _form = www.form.prepare_form(_form)
            try:
                resources = json.loads(_form.text)
            except:
                error = 'Bad json'
            if not error:
                print(resources)
                self.root.host.cmd_save('SET_HOST_RESOURCES', dict_(text=_form.text))
                raise cherrypy.HTTPRedirect('')

        if cherrypy.request.method=='GET' or error:
            if not error:
                sql = "select value from values where name='cfg_resources'"
                text = db.sql(sql, return_one=True).value
                _form = dict_(text=text)
            return self.root.render('/host/config/resources/edit', _form=_form,
                                    error=error)

