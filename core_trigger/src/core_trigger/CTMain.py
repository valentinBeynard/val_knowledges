#from core_trigger import CTConfiguration, CTServiceLauncher, CTService
import CTConfiguration, CTServiceLauncher, CTService


import time
import os

import socket




#####################################
# REGISTER SERVICES (request leading to actions)
# {request, call_function}
#####################################
REGISTER_SERVICES = { "LAUNCHER": CTServiceLauncher.CTServiceLauncher("Main Server launcher"),
                     "DEFAULT": CTService.CTService("Empty service")}

def main_server_power_on(on_signal_pin):
    # Assert PS-ON signal to low for less than 1s, starting the PSU
    on_signal_pin.on()
    time.sleep(0.5)
    on_signal_pin.off()

def get_WSGIAdapter_port():
    return int(CTConfiguration.getConf("WSGI_ADAPTOR_PORT"))

def WSGI_parser(m_request):
    
    # Service returned value
    service_output = 0
    
    # Get request radical and request data
    m_request =  m_request.split('_')
    
    # Assert that there are 2 elements: radical and data
    if len(m_request) > 1:
        m_request_rad =  m_request[0]
        m_request_data =  m_request[1]
    else:
        return -1

    # Execute corresponding service if request match with REGISTERED SERVICES
    if m_request_rad in REGISTER_SERVICES.keys():
        service_output = REGISTER_SERVICES.get(m_request_rad).run(m_request_data)

    return service_output

"""
    Test URL : http://dnsval.vbeynard.fr:1203/gateway?auth_key=GillietBeynard!&pck_rq=CMD_LAUNCH&pck_key=123456
"""
def main():
    
    # Create socket to connect to WSGI gateway
    wsgiGateway_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set socket in TIMEOUT mode (5s) instead of default BLOCKING mode
    wsgiGateway_socket.settimeout(5.0)
    # WSGI request received
    wsgiRequest = 0
    # Return request to WSGI adapter
    wsgi_return_request = 0 
      
    CTConfiguration.initConf()

    # Setup registered services
    for service_name, service in REGISTER_SERVICES.items():
        service.setup()

    # Bind socket to all available interfaces on port "TRIGGER_SERVER_PORT"
    dbg_port = get_WSGIAdapter_port()
    print(dbg_port)
    wsgiGateway_socket.bind(('127.0.0.1', dbg_port))

    while 1:
        
        #####################################
        # PARSE WSGI REQUEST
        #####################################
        
        # Enable listening on socket
        wsgiGateway_socket.listen()
        
        # Try/except catch to handle TIMEOUT condition
        try:
            # Waiting for WSGI Adapter connection. Timeout 5s
            conn_socket, addr = wsgiGateway_socket.accept()
            
            print('Connection entrance from: ', addr)
            
            # Receive max 1024 bytes from WSGI Adapter client connected
            wsgiRequest = conn_socket.recv(1024)
            
            # Cast in str
            wsgiRequest = wsgiRequest.decode()
            
            print("CTMain request = " + wsgiRequest)
            
            # Parse request and execute associate service
            wsgi_return_request = WSGI_parser(wsgiRequest)
            
            # Send returned value to WSGI adapter
            wsgi_return_request = str(wsgi_return_request).encode()
            conn_socket.send(wsgi_return_request)
            
        except socket.timeout:
            print("Timeout")
            pass


if __name__ == '__main__':
    main()