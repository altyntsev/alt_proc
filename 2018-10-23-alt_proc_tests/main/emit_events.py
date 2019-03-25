import alt_path
from _header import *
import random
import string

script.start()

print('periodic', alt.time.now())

# time.sleep(20)

# script.error('error1')
# script.error('error2')

param = "".join(random.choice(string.ascii_letters) for x in range(10))
script.emit_event('test-basic', param)

# for i in range(2):
#     param = "".join(random.choice(string.ascii_letters) for x in range(10))
#     script.emit_event('test-resources', param)

script.exit()

