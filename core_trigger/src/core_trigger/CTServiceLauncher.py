'''
Created on 29 juil. 2023

@author: valbe
'''

#from core_trigger import CTService, CTConfiguration
import CTService, CTConfiguration

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
        
        
    def setup(self):
        
        self.mainServer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set socket in TIMEOUT mode (5s) instead of default BLOCKING mode
        self.mainServer_socket.settimeout(5.0)
        
        # Init ON signal pin
        self.on_signal_pin = self.init_on_signal_pin()
        
        # Go to iddle
        self.state = self.state_list.get('IDDLE')
        
    def run(self, m_request_data):
            
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
                        
            if m_request_data == 'STARTING':
                self.state = self.state_list.get('STARTING')

        #####################################
        # STARTING STATE
        #####################################             
        if self.state == self.state_list.get('STARTING'):
            
            # Power ON the main server
            # main_server_power_on
            
            # Bind socket to all available interfaces on port "MAIN_SERVER_PORT"
            self.mainServer_socket.bind(('', self.get_port()))
            # Enable listening on socket
            self.mainServer_socket.listen()
            
            # Try/except catch to handle TIMEOUT condition
            try:
                conn_socket, addr = self.mainServer_socket.accept()
            
                print('Connection entrance from: ', addr)
            
                # Receive max 1024 bytes from client connected
                sck_data = conn_socket.recv(1024)
                
                if(sck_data == b'IsUp'):
                    print('Main Server is Up now !')
                    self.state = self.state_list.get('RUNNING')

            except socket.timeout:
                print('Main Server did not answered !')
            
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