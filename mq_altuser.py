import pymqi

queue_manager = 'QM1'
channel = 'DEV.APP3.SVRCONN'
host = '172.17.0.2'
port = '1414'
queue_name = 'DEV.QUEUE.1'
message = 'Hello from Python!'
alternate_user_id = 'mqm'
conn_info = '%s(%s)' % (host, port)

qmgr = pymqi.connect(queue_manager, channel, conn_info)

od = pymqi.OD()
od.ObjectName = queue_name
od.AlternateUserId = alternate_user_id

queue = pymqi.Queue(qmgr)
queue.open(od, pymqi.CMQC.MQOO_OUTPUT | pymqi.CMQC.MQOO_ALTERNATE_USER_AUTHORITY)
queue.put(message)

queue.close()
qmgr.disconnect()
