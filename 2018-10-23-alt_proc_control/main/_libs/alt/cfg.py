import yaml
import os
from alt.dict_ import dict_

def project_dir():

    file_path = __file__.replace('\\','/')
    main_pos = file_path.rfind('/main/')
    if main_pos==-1:
        raise Exception('Project dir not found')
    project_dir_ = file_path[:main_pos+1]

    return project_dir_

def main_dir():

    return project_dir() + 'main/'

def projects_dir():

    file_path = __file__.replace('\\','/')
    pos = file_path.rfind('/projects/')
    if pos==-1:
        raise Exception('Projects dir not found')
    projects_dir_ = file_path[:pos] + '/projects/'

    return projects_dir_

def root_dir():

    return os.path.abspath(projects_dir() + '..').replace('\\','/') + '/'

def read(cfg_name='_main'):

    if '~' in cfg_name:
        cfg_name = os.path.expanduser(cfg_name)

    if os.path.exists(cfg_name):
        cfg_file = cfg_name
    else:
        cfg_file = main_dir() + '_cfg/' + cfg_name + '.cfg'
    host_cfg_file = cfg_file.replace('.cfg','__%s.cfg' % host())

    if not os.path.exists(cfg_file) and not os.path.exists(host_cfg_file):
        raise Exception('Cfg file not exists', cfg_name)

    cfg = dict_()
    if os.path.exists(cfg_file):
        with open(cfg_file) as f:
            cfg = yaml.load(f)
            if cfg is None:
                cfg = dict_()

    if os.path.exists(host_cfg_file):
        with open(host_cfg_file) as f:
            host_cfg = yaml.load(f)
            if host_cfg is not None:
                cfg.update(host_cfg)

    return dict_(cfg)

def read_global(cfg_name):

    cfg_file = project_dir() + '../_cfg/' + cfg_name + '.cfg'

    return read(cfg_file)

def host():

    host_cfg_file = project_dir() + '../_cfg/host.cfg'
    with open(host_cfg_file) as f:
        cfg = yaml.load(f)

    return cfg['name']

def user():

    return read_global('user').name

def rep():

    s = main_dir().split('/')
    rep = s[-4]

    if rep=='projects':
        rep = '_local'

    return rep

def project():

    s = main_dir().split('/')

    return s[-3]

def app():

    return user() + '-' + rep() + '-' + project()
