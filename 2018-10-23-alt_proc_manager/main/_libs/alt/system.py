import subprocess, sys, traceback, os

def run(cmd, shell=False, wd=None, executable=None, wait=True):
    
    if isinstance(cmd,list):
        cmd = ';'.join(cmd)
    
    cmd = str(cmd)    
    print('Running :' + cmd)
    
    if os.name=='nt':
        if not wait:
            subprocess.Popen(str(cmd), shell=shell, cwd=wd)
        else:    
            out = subprocess.check_output(str(cmd), shell=shell, cwd=wd)
    else:
        if shell:
            executable='/bin/bash'
        else:
            cmd = cmd.split(' ')
        out = subprocess.check_output(cmd, shell=shell, cwd=wd, executable=executable)

    print(out)
    return out

def add_path(relpath):
    
    caller_path = traceback.extract_stack()[-2][0]
    #print caller_path
    path = os.path.abspath( os.path.dirname(caller_path) + '/' + relpath)
    #print path
    if path not in sys.path:
        sys.path.append( path )
    
