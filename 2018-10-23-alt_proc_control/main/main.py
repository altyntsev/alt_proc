import alt_path
from header import *
from cherrypy import _cperror
from host import Host
import db_lib

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

    cherrypy.thread_data.db = db_lib.DB()

cherrypy.engine.subscribe('start_thread', connect)

class Root(object):

    _cp_config = {}

    def __init__(self):

        cherrypy.log.screen = False
        self.main_dir = main_dir
        self.cfg = cfg
        self.app = app
        self.env = jinja2.Environment(loader = jinja2.FileSystemLoader(self.main_dir + 'tpls'))
        self.production = cfg.get('production', False)
        if self.production:
            self._cp_config['request.error_response'] = handle_error

        self.host = Host(self)

        print(alt.time.now_iso(), '%s started at %s' % (app, cfg.root_url) )

    def get_user(self):

        if self.production:
            if 'user' not in cherrypy.session:
                return None
            else:
                if cherrypy.session['user'].name=='debug':
                    del cherrypy.session['user']
                    return None
                return cherrypy.session['user']
        else:
             user = dict_(name='debug', roles=['admin'])

        return user

    def render(self, tpl_name, **kwargs):

        kwargs = dict_(kwargs)
        user = self.get_user()
        if user:
            kwargs._user = user.name
            kwargs._roles = user.roles
        else:
            raise cherrypy.HTTPRedirect('/login')
        kwargs._root = self.cfg.root_url
        kwargs._form = json.dumps(kwargs.get('_form', {}))
        kwargs._production = self.production
        if not kwargs.get('host'):
            kwargs.host = ''
        tpl = self.env.get_template(tpl_name + '.tpl')

        return tpl.render(kwargs)

    def auth(self, role=None):

        if not 'user' in cherrypy.session:
            if 'login_url' in cherrypy.session:
                del cherrypy.session['login_url']
            if 'login' not in cherrypy.url():
                cherrypy.session['login_url'] = cherrypy.url()
            raise cherrypy.HTTPRedirect('/login')

        user = self.get_user()
        if role not in user.roles:
            raise cherrypy.HTTPRedirect('/error/auth/')

    @cherrypy.expose
    def login(self, name=None, pwd=None):

        error = None
        if cherrypy.request.method=='POST':
            users = alt.cfg.secure(app).users
            md5 = hashlib.md5(pwd.encode('utf-8')).hexdigest()
            for user in users:
                if user.name==name and user.pwd==md5:
                    cherrypy.session['user'] = user
                    raise cherrypy.HTTPRedirect(cherrypy.session.get('login_url','/'))
            error = 'Логин неверен'

        if error or cherrypy.request.method=='GET':
            tpl = self.env.get_template('login.tpl')
            return tpl.render(user=name, pwd=pwd, error=error)

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
            msg = 'Нет прав'
        if msg is None:
            msg = 'Неизвестная ошибка'

        return self.render('main', error=msg)

    @cherrypy.expose
    def index(self):

        if not self.cfg.hub:
            url = '/host/jobs/last/localhost/'
        raise cherrypy.HTTPRedirect(url)

main_dir = alt.cfg.main_dir()
cfg = alt.cfg.read()
app = cfg.get('app', alt.cfg.app())
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