import pymqi
import os

import time

def as_unix_user(uid, gid=None):  # optional group
    def wrapper(func):
        def wrapped(*args, **kwargs):
            pid = os.fork()
            if pid == 0:  # we're in the forked process
                if gid is not None:  # GID change requested as well
                    os.setgid(gid)
                os.setuid(uid)  # set the UID for the code within the `with` block
                func(*args, **kwargs)  # execute the function
                os._exit(0)  # exit the child process
        return wrapped
    return wrapper



def name_change(oldname, newname):
	bashCommand = "usermod -l " + newname + " " + oldname
	os.system(bashCommand)
	

@as_unix_user(1001)
def attempt_connect():
	try:
		queue_manager = 'QM1'
		channel = 'SYSTEM.ADMIN.SVRCONN'
		host = '127.0.0.1'
		port = '1414'
		conn_info = '%s(%s)' % (host, port)
		qmgr = pymqi.connect(queue_manager, channel, conn_info)
		qmgr.disconnect()
		print("Connection Successful " + newname)
	except Exception:
		print("Connection Failed " + newname) 


first_name = 'ditto'
newname = 'ditto'
attempt_connect()
time.sleep(1)
name_list = ["admin", "mqm"]

for name in name_list:
	oldname = newname
	newname = name
	name_change(oldname, newname)
	attempt_connect() 
	time.sleep(1)


name_change(newname, first_name)