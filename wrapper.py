import uuid
import time
import os
while True:
    cmd = './ace0 {}'.format(uuid.uuid4())
    os.popen(cmd)
    time.sleep(0.01)
