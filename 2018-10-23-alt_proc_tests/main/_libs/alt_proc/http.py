import subprocess
import os
from alt_proc.script import Script
import alt_proc.file
import alt.file

def curl(url, dest=None, user=None, pwd=None):
    
    options = ' -m 3600 --speed-limit 5000 ' #

    if dest:
        if os.path.exists(dest):
            return
        options += '--output %s ' % (dest + '.tmp')
    else:
        options += '--remote-name '

    if user:
        options += '--user %s:%s' % (user, pwd)

    cmd = 'curl %s "%s"' % (options, url)
    print(cmd)
    try:
        subprocess.check_call(cmd, shell=True)
    except:
        script = Script()
        script.fatal('Curl failed', restart_after=1)

    if dest:
        alt.file.move(dest + '.tmp', dest)