import alt_path
from header import *
import db_lib

print('Install')

db = db_lib.connect()

# db.sql( alt.file.read(main_dir + 'install/host.sql') )

values = db_lib.Values(db)

db.sql("delete from values")
db.sql("insert into values values ('manager_mtime', %s)", alt.time.now_iso(), return_id=False)
db.sql("insert into values values ('host_status', 'ACTIVE')", return_id=False)
db.sql("insert into values values ('cfg_msgs', '')", return_id=False)
db.sql("insert into values values ('cfg_resources', '{}')", return_id=False)

print('Done')