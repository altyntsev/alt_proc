import alt_path
from header import *
import db_lib

print('Test Init')

db = db_lib.connect()

alt_proc_wd = os.path.abspath(os.getcwd() + '/..').replace('\\','/') + '/'
alt.file.delete(alt_proc_wd + 'jobs/')
for table in ['runs','events','cmds','msgs','scripts','jobs','tasks']:
    db.sql("DELETE from %s" % table)
db.sql("insert into tasks (name, project, type, period, status) values "
            "('scan', '2018-10-23-alt_proc_tests', 'PERIODIC', 1, 'ACTIVE'), "
            "('simple', '2018-10-23-alt_proc_tests', 'EVENT', NULL, 'ACTIVE')")
values = db_lib.Values(db)
values['host_status'] = 'RUN'
values['cfg_msgs'] = ''

print('Done')