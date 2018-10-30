import hashlib
import getpass

pwd = getpass.getpass('Password:')
md5 = hashlib.md5(pwd.encode('utf-8')).hexdigest()
print('MD5:', md5)
