import shutil, os, glob, re
from alt.dict_ import dict_
import alt.system 
import traceback, platform, ctypes, pickle

def name_ext(filename):
    
    filename = slash(filename)
    
    pos0 = filename.rfind('/')+1
    if pos0==0:
        pos0 = filename.rfind('\\')+1
    return filename[pos0:]               

def ext(filename):
    
    filename = slash(filename)
    
    pos0 = filename.rfind('.')
    if pos0==-1:
        return ''
    return filename[pos0+1:]
        
def name(filename):
    
    filename = slash(filename)
    
    if isdir(filename):
        filename = filename[:-1]
        
    pos0 = filename.rfind('/')+1
    if pos0==0:
        pos0 = filename.rfind('\\')+1

    pos1 = filename.rfind('.')
    if pos1==-1 or pos1<pos0:
        pos1 = len(filename)

    return filename[pos0:pos1]        
    
def isdir(name):
    
    if name[-1]=='\\' or name[-1]=='/':
        return True
    else:
        return False
    
def prepare_src_dest(src, dest, overwrite=False, makedir=True):
    
    script = Proc()
    
    if isinstance(src,(str,unicode)):
        if re.search(r'[*?]', src): # mask
            srclist = glob.glob(src)
            if not srclist:
                print('Nothing to copy/move')
                return (None,None)
            if not isinstance(dest,(str,unicode)):
                raise Exception('Destination is not a string')
            if not isdir(dest):
                raise Exception('Destination is not a directory',dest)
        else:
            srclist = [src]

    if isinstance(src,list):
        srclist = src
        
    if isinstance(dest,(str,unicode)):
        if isdir(dest):
            if not exists(dest) and not makedir:
                if script:
                    script.warn('Destination does not exists', dict_(dest=dest) )
                    script.exit(restart_after = 5)
                else:    
                    raise Exception('Destination does not exists',dest)
            else:
                mkdir(dest)
            destlist = []
            for srcfile in srclist:
                destfile = dest + os.path.basename(srcfile)
                if os.path.exists(destfile) and not overwrite:
                    destlist.append('')
                    print('Destination file exists', destfile) 
                else:
                    destlist.append(destfile)
        else:
            destlist = [dest]
            
    if isinstance(dest,list):
        destlist = dest
        
    return (srclist,destlist)            
    
def copy(src, dest, overwrite=True, makedir=True):
    
    srclist, destlist = prepare_src_dest(src, dest, overwrite=overwrite, makedir=makedir)
    if not srclist:
        return

    for i, srcfile in enumerate(srclist):
        if destlist[i]=='':
            continue
        destfile = destlist[i]
        print('Copying ', srcfile, destfile)
        shutil.copy2( srcfile, destfile + '~')
        shutil.move( destfile + '~', destfile)
                    
def move(src, dest):
    
    srclist, destlist = prepare_src_dest(src, dest)
    if not srclist:
        return
    
    for i, srcfile in enumerate(srclist):
        if destlist[i]=='':
            continue
        print('Moving ', srcfile, destlist[i])
        shutil.move(srcfile, destlist[i])
    
def mkdir(dir):
    
    if not os.path.exists(dir):
        os.makedirs(dir)
        
def delete(mask, ignore=False):
    
    if isdir(mask) or os.path.isdir(mask):
        if not os.path.exists(mask):
            return
        try:
            shutil.rmtree(mask)
        except Exception:
            if ignore:
                print('Can not delete ' + mask)
            else:
                raise
    else:    
        for file in glob.glob(mask):
            try:
                os.remove(file)
            except Exception:
                if ignore:
                    print('Can not delete ' + mask)
                else:
                    raise
        
def exists(src):
    
    if not isinstance(src,(str,unicode)):
        raise Exception('Arg is not a string')
    if isdir(src):
        return os.path.exists(src[:-1])
    else:
        return os.path.exists(src)
    
def clear(directory, exclude=[]):
    
    if not isdir(directory):
        raise Exception('Arg is not a directory')
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            if file in exclude:
                continue
            os.remove(os.path.join(root,file))
        for dir in dirs:
            os.rmdir(os.path.join(root,dir))
            
def dir(path):
    
    return os.path.dirname(path) + '/'

def delivery(src,dest,metadata=True):
    
    srclist, destlist = prepare_src_dest(src, dest)
    if not srclist:
        return

    for i, srcfile in enumerate(srclist):
        try:
            if destlist[i]=='':
                continue
            destfile = destlist[i]
            print('Copying ', srcfile, destfile)
            if metadata:
                shutil.copy2( srcfile, destfile + '~')
            else:    
                shutil.copyfile( srcfile, destfile + '~')
            shutil.move( destfile + '~', destfile)
        except Exception:
            script = Proc()
            traceback.print_exc()
            script.warn('Failed to copy', dict_(srcfile=srcfile, destfile=destfile) )
            script.exit(restart_after=5)
            
def zip(zip_file, zip_list):
    
    script = Proc()
    if not isinstance(zip_list,list):
        raise Exception('zip_list must be list')
    if os.name=='nt':
        cmd = script.root_dir + 'soft/7-zip/7z a -bd %s %s' % (zip_file, ' '.join(zip_list))
    else:    
        cmd = 'zip -j %s %s' % (zip_file, ' '.join(zip_list))
    system.run(cmd)    

def unzip(zip_file,out_dir,include='*'):
    
    script = Proc()
    include = ' '.join(include) 
    cmd = script.root_dir + 'soft/7-Zip/7z.exe e -r -y -o%s %s %s' % \
        (out_dir,zip_file,include)
    system.run(cmd)     
    
def slash(path):
    
    return path.replace('\\','/')

def touch(filename):

    mkdir( dir(filename) )    
    open(filename,'w').close()
    
def size(path):
    
    if isdir(path) or os.path.isdir(path):
        sz = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                sz += os.stat(root + '/' + file).st_size
    else:
        sz = os.stat(path).st_size

    return sz

def free_space(folder):

    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        free = free_bytes.value
    else:
        st = os.statvfs(folder)
        free = st.f_bavail * st.f_frsize

    return int(free/1e9)

def dump(filename, data):
    
    with open(filename,'wb') as f:
        cPickle.dump(data, f)
    
def load(filename):
    
    if not exists(filename):
        return None
    with open(filename,'rb') as f:
        data = cPickle.load(f)
    return data
    
def file_mtime_iso(filename):

    from datetime import datetime

    mtime = os.stat(filename).st_mtime
    mtime = datetime.fromtimestamp(mtime)
    return mtime.strftime('%Y-%m-%d %H:%M:%S')

def read(filename):
    
    with open(filename) as f:
        return f.read()

def write(filename, text):
    
    if isinstance(text, list):
        text = '\n'.join(text)
    
    with open(filename,'w') as f:
        f.write(text)
    
def readlines(filename):
    
    with open(filename) as f:
        
        return f.readlines()
    
def abspath(path):

    abspath_ = os.path.abspath(path).replace('\\','/').replace('//','/')
    if path[-1] in ['\\','/']:
        abspath_ += '/'

    return abspath_

def wd():

    return abspath(os.getcwd() + '/')
    
    
    
    
    
    
    
    
    
    
    
    
    