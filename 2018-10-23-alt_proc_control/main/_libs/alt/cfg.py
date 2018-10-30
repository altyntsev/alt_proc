import yaml
import os
import sys
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
    projects_dir_ = file_path[:pos+1] + '/projects/'

    return projects_dir_

def read(cfg_name='main'):

    if os.path.exists(cfg_name):
        cfg_file = cfg_name
    else:
        cfg_file = main_dir() + '_cfg/' + cfg_name + '.cfg'

    if os.path.exists(cfg_file):
        with open(cfg_file) as f:
            cfg = yaml.load(f)
    else:
        cfg = dict_()

    host_name = host()
    if host_name:
        host_cfg_file = cfg_file.replace('.cfg','__%s.cfg' % host_name)
        if not os.path.exists(cfg_file) and not os.path.exists(host_cfg_file):
            raise Exception('Cfg file not exists', cfg_name)
        if os.path.exists(host_cfg_file):
            with open(host_cfg_file) as f:
                host_cfg = yaml.load(f)
        else:
            host_cfg = dict_()

        cfg.update(host_cfg)

    return dict_(cfg)

def secure(cfg_name):

    cfg_file = os.path.expanduser('~/.sec/%s.cfg' % cfg_name)
    cfg = read(cfg_file)

    return cfg

def read_global(cfg_name):

    return read( projects_dir() + '_cfg/' + cfg_name + '.cfg' )

def host():

    cfg_file = projects_dir() + '_cfg/host.cfg'
    if not os.path.exists(cfg_file):
        return None

    with open(cfg_file) as f:
        cfg = yaml.load(f)

    return cfg['name']

def user():

    return read_global('user').name

def app():

    s = main_dir().split('/')

    return s[-4] + '-' + s[-3]
