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

    return os.path.abspath(project_dir() + '..').replace('\\','/') + '/'

def read(cfg_name='main'):

    if os.path.exists(cfg_name):
        cfg_file = cfg_name
    else:
        cfg_file = main_dir() + '_cfg/' + cfg_name + '.cfg'
        if not os.path.exists(cfg_file):
            cfg_file = main_dir() + '_cfg/' + cfg_name + '__host.cfg'
            if not os.path.exists(cfg_file):
                raise Exception('Cfg file not exists', cfg_name)

    with open(cfg_file) as f:
        cfg = yaml.load(f)
    if not cfg:
        cfg = dict_()

    host_cfg_file = cfg_file.replace('.cfg','__host.cfg')
    if os.path.exists(host_cfg_file):
        with open(host_cfg_file) as f:
            host_cfg = yaml.load(f)
        if host_cfg:
            cfg.update(host_cfg)

    return dict_(cfg)

def secure(cfg_name):

    cfg_file = os.path.expanduser('~/.sec/%s.cfg' % cfg_name)
    cfg = read(cfg_file)

    return cfg

def read_global(cfg_name):

    return read(projects_dir() + '_cfg/' + cfg_name + '.cfg')

def root_dir():

    return os.path.abspath(projects_dir() + '..').replace('\\','/') + '/'

def host():

    return read(root_dir() + 'cfg/host.cfg').name

def user():

    return read_global('user').name

