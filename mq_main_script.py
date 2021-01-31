import argparse 
import pymqi
from mq_dump_conf import dump_all

arg_parser = argparse.ArgumentParser()


#REQUIRED
arg_parser.add_argument("--host", type=str, default="127.0.0.1")
arg_parser.add_argument("--port", type=str, default="1414")
arg_parser.add_argument("--queue_manager", type=str, default="QM1")
arg_parser.add_argument("--channel", type=str, default="SYSTEM.ADMIN.SVRCONN")

#AUTHENTICATION

#if client auth is none or optional, dont use --use_client_auth
#usermod -l [client_id] ditto
#sudo su [client_id]
#python3 mq_main_script.py
#usermod -l ditto [client_id] 

arg_parser.add_argument("--use_client_auth", action="store_true")
arg_parser.add_argument("--username", type=str, default="admin")
arg_parser.add_argument("--password", type=str, default="passw0rd")

#runmqakm -keydb -create -db server_cert.kdb -pw mainframe -type pkcs12 -expire 1000 -stash
#runmqakm -cert -add -label QM1.cert -db server_cert.kdb -stashed -trust enable -file server.crt
arg_parser.add_argument("--use_ssl", action="store_true")
arg_parser.add_argument("--cipherspec", type=str, default="TLS_RSA_WITH_AES_128_CBC_SHA256")
arg_parser.add_argument("--server_cert", type=str, default="server_cert")

#ACTIONS
arg_parser.add_argument("--browse_queue", action="store_true")
arg_parser.add_argument("--browse_queue_name", type=str, default="DEV.QUEUE.1")

arg_parser.add_argument("--dump_conf", action="store_true")
#SYSTEM.MQEXPLORER.REPLY.MODEL - MQ Explorer Reply Queue
#SYSTEM.MQSC.REPLY.QUEUE - Generic Command Replay Queue
arg_parser.add_argument("--reply_queue_name", type=str, default="SYSTEM.MQSC.REPLY.QUEUE")

#create a service by default run and delete it
arg_parser.add_argument("--make_service", action="store_true")
arg_parser.add_argument("--service_name", type=str, default="testserv")
arg_parser.add_argument("--start_cmd", type=str, default="/bin/mkdir")
arg_parser.add_argument("--start_args", type=str, default="/tmp/mkdir_test")
arg_parser.add_argument("--service_dont_run", action="store_true")
arg_parser.add_argument("--service_dont_delete", action="store_true")



args = arg_parser.parse_args()




def connect():
	global qmgr
	conn_info = '%s(%s)' % (args.host, args.port)
	if(not args.use_client_auth and not args.use_ssl):
		qmgr = pymqi.connect(args.queue_manager, args.channel, conn_info)
	elif(args.use_client_auth and not args.use_ssl):
		qmgr = pymqi.connect(args.queue_manager, args.channel, conn_info, args.username, args.password)
	elif(args.use_ssl):
		cd = pymqi.CD()
		cd.ChannelName = bytes(args.channel,encoding='utf8')
		cd.ConnectionName = bytes(conn_info,encoding='utf8')
		cd.ChannelType = pymqi.CMQC.MQCHT_CLNTCONN
		cd.TransportType = pymqi.CMQC.MQXPT_TCP
		cd.SSLCipherSpec = bytes(args.cipherspec,encoding='utf8')
		sco = pymqi.SCO()
		sco.KeyRepository = bytes(args.server_cert,encoding='utf8')
		qmgr = pymqi.QueueManager(None)
		if(not args.use_client_auth):
			qmgr.connect_with_options(args.queue_manager, cd=cd, sco=sco)
		else:
			qmgr.connect_with_options(args.queue_manager, cd=cd, sco=sco,user=bytes(args.username,encoding='utf8'), password=bytes(args.password,encoding='utf8'))
	print("connection succesful")




def browse_queue():
	queue = pymqi.Queue(qmgr, str(args.browse_queue_name), pymqi.CMQC.MQOO_BROWSE)

	current_options = pymqi.GMO()
	current_options.Options = pymqi.CMQC.MQGMO_BROWSE_FIRST 

	md = pymqi.MD()
	message = queue.get(None, md, current_options)
	print("Browsing Top Message Of " + str(args.browse_queue_name))
	print(str(message))

def make_service():
	service_create_pcf_arg = {
        pymqi.CMQC.MQCA_SERVICE_NAME: args.service_name,
        pymqi.CMQC.MQIA_SERVICE_CONTROL: pymqi.CMQC.MQSVC_CONTROL_MANUAL,
        pymqi.CMQC.MQIA_SERVICE_TYPE: pymqi.CMQC.MQSVC_TYPE_COMMAND,
        pymqi.CMQC.MQCA_SERVICE_START_COMMAND: bytes(args.start_cmd,encoding='utf8'),
        pymqi.CMQC.MQCA_SERVICE_START_ARGS: bytes(args.start_args,encoding='utf8'),}
	pcf = pymqi.PCFExecute(qmgr)
	pcf.MQCMD_CREATE_SERVICE(service_create_pcf_arg)
	service_pcf_arg = {pymqi.CMQC.MQCA_SERVICE_NAME: args.service_name}
	if(not args.service_dont_run):
		pcf.MQCMD_START_SERVICE(service_pcf_arg)
	if(not args.service_dont_delete):
		pcf.MQCMD_DELETE_SERVICE(service_pcf_arg)


def main(): 
	connect()
	if(args.browse_queue):
		browse_queue()
	if(args.dump_conf):
		dump_all(qmgr,bytes(args.reply_queue_name,encoding='utf8'))
	if (args.make_service):
		make_service()
	qmgr.disconnect()


if __name__ == "__main__":
    main()







