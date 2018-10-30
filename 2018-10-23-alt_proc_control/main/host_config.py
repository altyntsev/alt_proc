import alt_path
from header import *

class Config:

    class Tasks:

        def __init__(self, root):

            self.root = root

        def render(self, host, tpl_name, **kwargs):

            return self.root.render(host, 'host/config/tasks/' + tpl_name, **kwargs)

        def list(self, host, db):

            tasks = db.sql("select * from tasks")

            return self.render(host, 'list', tasks=tasks)

        def edit(self, host, task_id, form=None, type=None):

            default = dict_(n_fatals=1, n_runs=1)
            form = www.form.prepare_form(form)
            error = None

            if cherrypy.request.method=='POST':
                if task_id=='new':
                    if db.sql("select * from tasks where name=%s", form.name):
                        error = 'Task name exists'
                if not error:
                    task = form
                    task.id = task_id
                    cmd = 'NEW_TASK' if task_id=='new' else 'EDIT_TASK'
                    self.root.host.cmd(host, cmd, task)
                    self.root.redirect(host, '/config/tasks/')

            if cherrypy.request.method=='GET' or error:
                if task_id!='new':
                    task = db.sql("select * from tasks where id=%s", task_id)[0]
                else:
                    task = dict_(type=type)
                if not error:
                    form = task
                return self.render(host, 'edit_' + task.type, form=form, task_id=task_id, task=task,
                                   type=type)

    class Msgs:

        def __init__(self, root):

            self.root = root

        def edit(self, host, form=None):

            error = None
            if cherrypy.request.method=='POST':
                form = www.form.prepare_form(form)
                for i, line in enumerate(form.text.split('\n')):
                    if not line.strip():
                        continue
                    m = re.match('([+-] *(.+?) *(.+?) *\"(.+?)\" *(.*))', line)
                    if not m:
                        error = 'Wrong format in line %s' % (i+1)
                if not error:
                    self.root.host.cmd(host, 'SET_CFG_MSG', dict_(text=form.text))
                    raise cherrypy.HTTPRedirect('/config/msgs/')

            if cherrypy.request.method=='GET' or error:
                if not error:
                    sql = "select value from values where name='config_msgs'"
                    text = db.sql(sql)[0].value
                    form = dict_(text=text)
                return self.root.render(host, '/host/config/msgs/edit', form=form, error=error)

    def __init__(self, root):

        self.root = root

        self.tasks = Config.Tasks(root)
        self.msgs = Config.Msgs(root)

