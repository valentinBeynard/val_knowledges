'''
Created on 29 juil. 2023

@author: valbe
'''

from podServer.core_trigger import CTService, CTConfiguration
#import CTService, CTConfiguration

import socket

# To use Raspberry GPIO. Library only on Raspberry target
from gpiozero import OutputDevice

class CTServiceLauncher(CTService.CTService):
    '''
    classdocs
    '''


    def __init__(self, m_name):
        '''
        Constructor
        '''
        
        CTService.CTService.__init__(self, m_name)
        self.state_list = {'INIT': 0,
                     'IDDLE': 1,
                     'STARTING': 'STARTING',
                     'RUNNING': 3,
                     'STOPPING': 4}
        
        self.state = 'DEFAULT_IDDLE'
    
        #####################################
        # SERVICE RELATED VARIABLES
        #####################################
        
        self.on_signal_pin = 0
        
        # Create socket to connect to main server
        self.mainServer_socket = 0
        
        # Connection socket created when mainServer_socket accept() connection from mainServer
        self.mainServer_conn_socket = 0
        
        # True when main Server connects to Trigger Server
        self.mainServer_on = False
        # True when main Server and Trigger Server are synchronized
        self.mainServer_sync= False
        # Number of connection try with Main Server:
        self.mainServer_maxTry_cnt = 0 
        
        
    def setup(self):
        
        self.mainServer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set socket in TIMEOUT mode (5s) instead of default BLOCKING mode
        self.mainServer_socket.settimeout(5.0)
        
        # Init ON signal pin
        self.on_signal_pin = self.init_on_signal_pin()
        
        # Go to iddle
        self.state = self.state_list.get('IDDLE')
        
    def run(self, m_request_data):
            
        print(f"CTServiceLauncher received request ! : {m_request_data}")
        
        # Split state from data:
        m_request_data = m_request_data.split(":")
        rq_state = m_request_data[0]
        rq_data = m_request_data[1]
        
        service_ret = 0   
        #####################################
        # INIT STATE
        #####################################
        if self.state == self.state_list.get('INIT'):
                                    
            # Init ON signal pin
            self.on_signal_pin = self.init_on_signal_pin()
            
            # Go to iddle
            self.state = self.state_list.get('IDDLE')
        
        #####################################
        # IDDLE STATE
        #####################################
        if self.state == self.state_list.get('IDDLE'):
                        
            if rq_state == 'STARTING':
                self.state = self.state_list.get('STARTING')

        #####################################
        # STARTING STATE
        #####################################             
        if self.state == self.state_list.get('STARTING'):
            
            print("CTServiceLauncher is STARTING!")

            # Power ON the main server
            # main_server_power_on
            
            # Bind socket to all available interfaces on port "MAIN_SERVER_PORT"
            self.mainServer_socket.bind(('', self.get_port()))
            # Enable listening on socket
            self.mainServer_socket.listen()
            
            self.mainServer_maxTry_cnt = 0
            
            # Continue until Main Server is awake
            while not (self.mainServer_on and self.mainServer_sync):
                # Try/except catch to handle TIMEOUT condition on SOCKET connection
                try:
                    self.mainServer_conn_socket, addr = self.mainServer_socket.accept()
                
                    print('Connection entrance from: ', addr)
                
                    # Main server is ON and socket connected
                    self.mainServer_on = True
                
                except socket.timeout:
                    print('Unable to connect to Main Server... Retrying...')
                    
                # Try to synchronize both servers
                if self.mainServer_on:            
                    while not self.mainServer_sync:
                        # Try/except catch to handle TIMEOUT condition on SYNCHRONIZATION
                        try:
                            
                            # Receive max 1024 bytes from client connected
                            sck_data = self.mainServer_conn_socket.recv(1024)
                            sck_data = sck_data.decode()
                            print("sck_data = ", sck_data)
                            if(sck_data == 'CS_ack'):
                                print('Main Server is Up now !')
                                self.mainServer_sync = True
                                self.state = self.state_list.get('RUNNING')
                        except socket.timeout:
                            print('Main Server did not answered !')    
                        
                        self.mainServer_maxTry_cnt = self.mainServer_maxTry_cnt + 1
                        if self.mainServer_maxTry_cnt >= 10:
                            print("Fail to Sync. with mainServer after 10 tries !")
                            break
            
                # If do not succeed to connect with main Server, return to IDDLE_STATE
                self.mainServer_maxTry_cnt = self.mainServer_maxTry_cnt + 1
                if self.mainServer_maxTry_cnt >= 10:
                    print("Fail to connect/sync. with mainServer after 10 tries")
            
                    self.mainServer_conn_socket.close()
                    self.mainServer_socket.close()
                    
                    self.state = self.state_list.get('IDDLE')
                    break

            print("RUNNING DONE !")
            return service_ret
        
        #####################################
        # RUNNING STATE
        #####################################            
        if self.state == self.state_list.get('RUNNING'):
            
            # Receive max 1024 bytes from client connected
            sck_data = conn_socket.recv(1024)
            
            while sck_data != b'Stop':
                t = int.from_bytes(sck_data)
                print(t)
            
            self.state = self.state_list.get('STOPPING')
            
        #####################################
        # STOPPING STATE
        #####################################
        if self.state == self.state_list.get('STOPPING'):
            
            self.on_signal_pin.off()
            self.state = self.state_list.get('IDDLE')
    
        else:
            print()

        return service_ret


    def init_on_signal_pin(self):
        
        # Parse pin
        pin = int(CTConfiguration.getConf("ON_SIGNAL_PINOUT"))
        print("Pin (BCM) is : " + str(pin))
        
        # Create GPIO and save it in conf
        on_GPIO = OutputDevice(pin, active_high = True, initial_value = False)
        CTConfiguration.setConf("ON_SIGNAL_PINOUT", on_GPIO)
        
        # Return GPIO
        return CTConfiguration.getConf("ON_SIGNAL_PINOUT")

    def get_port(self):
        return int(CTConfiguration.getConf("MAIN_SERVER_PORT"))