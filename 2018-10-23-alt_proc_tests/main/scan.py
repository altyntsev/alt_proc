import alt_path
from header import *
import random
import string

script.start()

print('periodic', alt.time.mtime())

# time.sleep(20)

# script.error('error1')
# script.error('error2')

key = "".join(random.choice(string.ascii_letters) for x in range(10))
script.emit_event('simple', key)

script.exit()

