import pymqi
import mqpcf as mqpcf
import json



def pcf_run(qmgr,reply_queue_name,message):
    pcf = mqpcf.mqpcf()
    #  Set up the queue for putting to the admin queue
    hAdmin = pcf.get_h_admin_queue(qmgr)
    # get the reply to queue - uses model queue if non specified
    hReply = pcf.get_h_reply_queue(qmgr,queue=reply_queue_name)
    #hReply = pcf.get_h_reply_queue(qmgr,queue=b'SYSTEM.MQSC.REPLY.QUEUE')
    #hReply = pcf.get_h_reply_queue(qmgr,queue=b'SYSTEM.MQEXPLORER.REPLY.MODEL')
    md = pcf.create_admin_MD(hReplyToQ=hReply) 

    # issue the request
    hAdmin.put(message, md)

    # we now need to get the replies
    md = pymqi.MD()
    gmo = pymqi.GMO()
    gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING | pymqi.CMQC.MQGMO_CONVERT
    gmo.WaitInterval = 1000 # 1 seconds
    output = []
    try:
        # loop around looking for messages
        # Once a message has been got, get the rest of messages with the same msgid
        # and correlid
        # if no more messages, then need to clear these fields to get next available
        # messages 
        # for i in range(100): 
        while True:
            data = hReply.get(None,md, gmo )
            md.set(MsgId=b'') # clear this so we get rest of messages in group
            header, data = pcf.parse_data(buffer=data, strip="yes", debug=0)
            if (header["Reason"] != 0):
                mqpcf.eprint("Reason mqcode:",pcf.header["sReason"])
                mqpcf.eprint("error return:",header)
                
            if header["Control"] == "LAST":
                md.set(MsgId=b'')
                md.set(CorrelId=b'')
            ret = data
            
            js = json.dumps(ret)
            output.append(js)
            
            # dumpData(data) 
    except pymqi.MQMIError as e:
        if (e.reason) != 2033: 
            print("exception :",e, e.comp, e.reason)

    hAdmin.close()
    hReply.close()
    return output

def parse_auth_info(AUTHINFO_LIST):
    for message in AUTHINFO_LIST:
        message = message.replace('"ADOPT_CONTEXT": 1', '"ADOPT_CONTEXT": YES')
        message = message.replace('"ADOPT_CONTEXT": 0', '"ADOPT_CONTEXT": NO')

        message = message.replace('"CHECK_LOCAL_BINDING": 0', '"CHECK_LOCAL_BINDING": OPTIONAL')
        message = message.replace('"CHECK_LOCAL_BINDING": 1', '"CHECK_LOCAL_BINDING": NONE')
        message = message.replace('"CHECK_LOCAL_BINDING": 2', '"CHECK_LOCAL_BINDING": REQADM')
        message = message.replace('"CHECK_LOCAL_BINDING": 3', '"CHECK_LOCAL_BINDING": REQUIRED')

        message = message.replace('"CHECK_CLIENT_BINDING": 0', '"CHECK_CLIENT_BINDING": OPTIONAL')
        message = message.replace('"CHECK_CLIENT_BINDING": 1', '"CHECK_CLIENT_BINDING": NONE')
        message = message.replace('"CHECK_CLIENT_BINDING": 2', '"CHECK_CLIENT_BINDING": REQADM')
        message = message.replace('"CHECK_CLIENT_BINDING": 3', '"CHECK_CLIENT_BINDING": REQUIRED')
        print(message)


def dump_all(qmgr, reply_queue_name):
    pcf = mqpcf.mqpcf()

    message = pcf.create_request("INQUIRE_Q_MGR")
    QMGR_ARGS = pcf_run(qmgr,reply_queue_name,message)
    for message in QMGR_ARGS:
        print(message)

    message = pcf.create_request("INQUIRE_CHANNEL",{"CHANNEL_NAME":'*'})
    CHANNEL_LIST = pcf_run(qmgr,reply_queue_name,message)
    for message in CHANNEL_LIST:
        print(message)

    message = pcf.create_request("INQUIRE_CHLAUTH_RECS",{"CHANNEL_NAME":'*'})
    CHLAUTH_LIST = pcf_run(qmgr,reply_queue_name,message)
    for message in CHLAUTH_LIST:
        print(message)

    message = pcf.create_request("INQUIRE_AUTH_INFO",{"AUTH_INFO_NAME":'*'})
    AUTHINFO_LIST = pcf_run(qmgr,reply_queue_name,message)
    parse_auth_info(AUTHINFO_LIST)





#INQUIRE_AUTH_INFO
