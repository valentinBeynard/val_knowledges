
# To use Raspberry GPIO
from gpiozero import OutputDevice

import time
import os

import socket

CONFIG_PATH = "./trigger_server.conf"

SERVER_FSM_STATES = {'INIT': 0,
                     'IDDLE': 1,
                     'STARTING': 2,
                     'RUNNING': 3,
                     'STOPPING': 4}

configuration_dict = {"MAIN_SERVER_IP" : "127.0.0.1",
                      "MAIN_SERVER_PORT" : "1204",
                      "WSGI_ADAPTOR_PORT" : "1205",
                      "POLLING_TIME_MS" : "6000",
                      "LAUNCHER_FILE" : "launching.ts",
                      "ON_SIGNAL_PINOUT" : "4"}

def create_conf_file():
    conf_file = open(CONFIG_PATH, 'wr')
    conf_file.write("MAIN_SERVER_IP=")
    conf_file.write("POLLING_TIME_MS=6000")
    print("Configuration file created !")
    return conf_file

def get_polling_time_s():
    return float(configuration_dict.get("POLLING_TIME_MS")) / 1000

def init_on_signal_pin():
    
    # Parse pin
    pin = int(configuration_dict.get("ON_SIGNAL_PINOUT"))
    print("Pin (BCM) is : " + str(pin))
    
    configuration_dict["ON_SIGNAL_PINOUT"] = OutputDevice(pin, active_high = True, initial_value = False)
    
    return configuration_dict["ON_SIGNAL_PINOUT"]

def main_server_power_on(on_signal_pin):
    # Assert PS-ON signal to low for less than 1s, starting the PSU
    on_signal_pin.on()
    time.sleep(0.5)
    on_signal_pin.off()
    
def get_port():
    return int(configuration_dict.get("MAIN_SERVER_PORT"))

def get_WSGIAdapter_port():
    return int(configuration_dict.get("WSGI_ADAPTOR_PORT"))


def main():
    
    fsm_state = 0
    old_fsm_state = fsm_state
    main_server_on = False

    main_server_ip = "127.0.0.1"
    polling_time_ms = 1000

    on_signal_pin = None
    
    # Create socket to connect to main server
    mainServer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Create socket to connect to WSGI gateway
    wsgiGateway_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        
    sck_data = 0
    
    t = 0

    while 1:
        
        #####################################
        # INIT STATE
        #####################################
        if fsm_state == SERVER_FSM_STATES.get('INIT'):
            
            # Load configuration
            try:
                conf_file = open(CONFIG_PATH, 'r')
            except IOError:
                print("Error: File does not appear to exist. Creating one")
                conf_file = create_conf_file()
            
            # Parse configuration
            for line in conf_file:
                line = line.split('=')
                
                # Find if exist in configuration
                if line[0] in configuration_dict.keys():
                    configuration_dict[line[0]] = line[1]
                else:
                    print("Error: Bad configuration line !")
                        
            # Init ON signal pin
            on_signal_pin = init_on_signal_pin()
            
            fsm_state = SERVER_FSM_STATES.get('IDDLE')
        
        #####################################
        # IDDLE STATE
        #####################################
        elif fsm_state == SERVER_FSM_STATES.get('IDDLE'):
            
            # Bind socket to all available interfaces on port "TRIGGER_SERVER_PORT"
            wsgiGateway_socket.bind(('', get_WSGIAdapter_port()))
            
            # Enable listening on socket
            wsgiGateway_socket.listen()
            
            # Wait for LAUNCHING_CMD from WSGI adapter
            while 1:
                # Waiting for WSGI Adapter connection. Blocking
                conn_socket, addr = wsgiGateway_socket.accept()
                
                print('Connection entrance from: ', addr)
                
                # Receive max 1024 bytes from WSGI Adapter client connected
                sck_data = conn_socket.recv(1024)
                
                if sck_data == b'CMD_LAUNCH':
                    fsm_state = SERVER_FSM_STATES.get('STARTING')
                    break
                else:
                    print("Data were : " + sck_data)
                        
        #####################################
        # STARTING STATE
        #####################################             
        elif fsm_state == SERVER_FSM_STATES.get('STARTING'):
            
            # Power ON the main server
            # main_server_power_on
            
            # Close previous socket to WSGI
            
            # Bind socket to all available interfaces on port "MAIN_SERVER_PORT"
            mainServer_socket.bind(('', get_port()))
            # Enable listening on socket
            mainServer_socket.listen()
            
            # Waiting for client connection. Blocking
            conn_socket, addr = mainServer_socket.accept()
            
            print('Connection entrance from: ', addr)
            
            # Receive max 1024 bytes from client connected
            sck_data = conn_socket.recv(1024)
            
            if(sck_data == b'IsUp'):
                print('Main Server is Up now !')
                fsm_state = SERVER_FSM_STATES.get('RUNNING')
            

        #####################################
        # RUNNING STATE
        #####################################            
        elif fsm_state == SERVER_FSM_STATES.get('RUNNING'):
            
            # Receive max 1024 bytes from client connected
            sck_data = conn_socket.recv(1024)
            
            while sck_data != b'Stop':
                t = int.from_bytes(sck_data)
                print(t)
            
            fsm_state = SERVER_FSM_STATES.get('STOPPING')
            
        #####################################
        # STOPPING STATE
        #####################################
        elif fsm_state == SERVER_FSM_STATES.get('STOPPING'):
            
            on_signal_pin.off()
            fsm_state = SERVER_FSM_STATES.get('IDDLE')
    
        else:
            print()
        if old_fsm_state != fsm_state:
            old_fsm_state = fsm_state
            print("fsm_state = " + str(fsm_state))

    return

if __name__ == '__main__':
    main()