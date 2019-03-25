import alt_path
from header import *
from cherrypy import _cperror
from host import Host

def handle_error():
    cherrypy.response.status = 500
    cherrypy.response.body = bytes("<html><body>Sorry, an error occured</body></html>",
                                   encoding='utf-8')
    print('-'*80)
    print(datetime.now())
    print(_cperror.format_exc())
    with open('errors.log', 'a') as f:
        print('-'*80, file=f)
        print(datetime.now(), file=f)
        print(_cperror.format_exc(), file=f)

def connect(thread_index):

    pwd_file = alt.cfg.read_global('alt_proc').pwd_file
    pwd = alt.cfg.read(pwd_file).db.pwd
    db = alt.pg.DB(db='alt_proc', user='alt_proc', pwd=pwd, schema='alt_proc')
    cherrypy.thread_data.db = db

cherrypy.engine.subscribe('start_thread', connect)

class Root(object):

    _cp_config = {}

    def __init__(self):

        cherrypy.log.screen = False
        self.main_dir = main_dir
        self.cfg = cfg
        self.app = app
        self.env = jinja2.Environment(loader = jinja2.FileSystemLoader(self.main_dir + 'tpls'))
        if self.cfg.catch_errors:
            self._cp_config['request.error_response'] = handle_error

        self.host = Host(self)

        print(alt.time.now(), '%s started at %s' % (app, cfg.root_url) )

    @cherrypy.expose
    def index(self):

        url = self.cfg.root_url + '/host/status/'
        raise cherrypy.HTTPRedirect(url)

    def render(self, tpl_name, **kwargs):

        kwargs = dict_(kwargs)
        user = cherrypy.session.get('user')
        if user:
            kwargs._user = user.login
            kwargs._roles = user.roles
        else:
            raise cherrypy.HTTPRedirect('/login')
        kwargs._root = self.cfg.root_url
        kwargs._form = json.dumps(kwargs.get('_form', {}))
        db = cherrypy.thread_data.db
        kwargs.n_cmds = db.sql("select count(*) as n from cmds where status='WAIT'")[0].n

        kwargs.now = alt.time.now()
        tpl = self.env.get_template(tpl_name + '.tpl')

        return tpl.render(kwargs)

    def redirect(self, rel_url):

        raise cherrypy.HTTPRedirect(self.cfg.root_url + rel_url)

    def auth(self, role=None):

        if 'user' not in cherrypy.session:
            if 'login_url' in cherrypy.session:
                del cherrypy.session['login_url']
            if 'login' not in cherrypy.url():
                cherrypy.session['login_url'] = cherrypy.url()
            raise cherrypy.HTTPRedirect('/login')

        user = cherrypy.session.get('user')
        if role not in user.roles:
            raise cherrypy.HTTPRedirect('/error/auth/')

    @cherrypy.expose
    def login(self, login=None, pwd=None):

        error = None
        if cherrypy.request.method=='POST':
            users = alt.cfg.read(self.cfg.users_file).users
            for user in users:
                md5 = hashlib.md5(pwd.encode('utf-8')).hexdigest()
                if user.login==login and user.md5==md5:
                    cherrypy.session['user'] = user
                    raise cherrypy.HTTPRedirect(cherrypy.session.get('login_url','/'))
            else:
                error = 'Wrong login/password'

        if error or cherrypy.request.method=='GET':
            tpl = self.env.get_template('login.tpl')
            return tpl.render(user=login, pwd=pwd, error=error)

    @cherrypy.expose
    def logout(self):

        if 'user' in cherrypy.session:
            del cherrypy.session['user']
        if 'login_url' in cherrypy.session:
            del cherrypy.session['login_url']
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def error(self, type=None):

        msg = None
        if type=='auth':
            msg = 'No access'
        if msg is None:
            msg = 'Unknown error'

        return self.render('main', error=msg)

main_dir = alt.cfg.main_dir()
cfg = alt.cfg.read()
app = 'alt_proc'
alt.file.mkdir('sessions')

cherrypy_cfg = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': cfg.port,
        },
    '/': {
        'tools.sessions.on': True,
        'tools.sessions.name': app,
        'tools.sessions.storage_type': 'file',
        'tools.sessions.storage_path': 'sessions',
        'tools.sessions.timeout': 1440
        },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': main_dir + 'static'
        }
}
cherrypy.quickstart(Root(), '/', config = cherrypy_cfg)