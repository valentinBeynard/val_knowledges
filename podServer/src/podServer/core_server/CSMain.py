import time
import os

import socket

from podServer.core.Configuration import ConfigHandler
from podServer.core_server.CSRequestHandler import RequestHandler
# from CSRequestHandler import RequestHandler 

CONFIG_PATH = "./main_server.conf"

CONFIGURATION_DICT = {"CT_SERVER_IP" : "192.168.1.32",
                      "CT_SERVER_PORT" : "1204",
                      "POLLING_TIME_MS" : "1000",
                      "ACK_TO_CTSERVER" : "CS_ack"
                      }


#####################################
# REGISTER SERVICES (request leading to actions)
# {request, call_function}
#####################################
# REGISTER_SERVICES = { "LAUNCHER": CTServiceLauncher.CTServiceLauncher("Main Server launcher"),
#                      "DEFAULT": CTService.CTService("Empty service")}


def get_CTServer_port(m_conf):
    return int(m_conf.getConf("CT_SERVER_PORT"))

def get_CTServer_ip(m_conf):
    return m_conf.getConf("CT_SERVER_IP")

def get_CTServer_polling(m_conf):
    return int(m_conf.getConf("POLLING_TIME_MS"))

def get_CSServer_ack_symbol(m_conf):
    return m_conf.getConf("ACK_TO_CTSERVER")

 

"""
    Test URL : http://dnsval.vbeynard.fr:1203/gateway?auth_key=GillietBeynard!&pck_rq=LAUNCHER_STARTING&pck_key=123456
"""
def main():
    
    # Init configuration file
    conf = ConfigHandler(CONFIG_PATH, CONFIGURATION_DICT)
    conf.initConf()
    
    # Get CTServer port and IP to parse incoming packet from CTServer
    CTServer_port = get_CTServer_port(conf)
    CTServer_ip = get_CTServer_ip(conf)
    CSServer_Ack_symbol = get_CSServer_ack_symbol(conf)
    CTServer_polling_ms = get_CTServer_polling(conf)

    
    # Start the RequestHandler process that will poll for request from CTServer
    RHandler = RequestHandler(CTServer_ip,
                              CTServer_port,
                              CSServer_Ack_symbol,
                              CTServer_polling_ms
                              )
    

    while 1:
        
        #####################################
        # 
        #####################################
        
        # Check for CT server request to parse
        if RHandler.has_new_request():
            # Parsing to be done !
            RHandler.get_pending_request()
        else:
            pass


if __name__ == '__main__':
    main()