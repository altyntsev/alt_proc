import subprocess, sys, traceback, os

def run(cmd, shell=False, wd=None, executable=None, wait=True):
    
    if isinstance(cmd,list):
        cmd = ';'.join(cmd)
    
    cmd = str(cmd)    
    print('Running :' + cmd)
    
    if os.name=='nt':
        if not wait:
            subprocess.Popen(str(cmd), shell=shell, cwd=wd)
            return
        else:    
            try:    
                out = subprocess.check_output(str(cmd), shell=shell, cwd=wd)
            except subprocess.CalledProcessError as e:
                print("Error:", e.output)
            for s in out.decode("utf-8").split('\r\n'):
                print(s)
            if out:
                print(out)
                print('End of', cmd)
            return out
                
    else:
        
        stop

def add_path(relpath):
    
    caller_path = traceback.extract_stack()[-2][0]
    #print caller_path
    path = os.path.abspath( os.path.dirname(caller_path) + '/' + relpath)
    #print path
    if path not in sys.path:
        sys.path.append( path )
    
