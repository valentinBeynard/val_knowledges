'''
Created on 3 sept. 2023

@author: Valentin BEYNARD
'''
from multiprocessing import Process, Pipe
import socket
import time

class RequestHandler():
    '''
    classdocs
    '''

    def __init__(self, m_CTServer_ip, m_CTServer_port, m_CSServer_Ack_symbol, m_CTServer_polling_ms: float = 1.0):
        '''
        Constructor
        '''
        
        # List containing all incoming request from CTServer
        self.request_list = []
        
        # Pipe to transfer request from main process to polling process
        self.RHandler_pipe, self.process_pipe = Pipe()
        
        # Polling process
        self.process = Process(target=RHandler_run, args=(self.process_pipe,
                                                               m_CTServer_ip,
                                                               m_CTServer_port,
                                                               m_CSServer_Ack_symbol,
                                                               m_CTServer_polling_ms
                                                               )) 
        self.process.start()

    def has_new_request(self):
       
        # Check if there is data available in the pipe
        if self.RHandler_pipe.poll():
            return True
        else:
            return False
    
    def get_pending_request(self):
        return self.RHandler_pipe.recv()

def RHandler_run(m_process_pipe, m_CTServer_ip, m_CTServer_port, m_CSServer_Ack_symbol, m_CTServer_polling_ms):
  
    args_print = f"{m_CTServer_ip} | {m_CTServer_port}"
    print(args_print)
    # Create socket to connect to CT Server
    CTServer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set socket in TIMEOUT when trying to connect/recv to/from CTServer
    CTServer_socket.settimeout(m_CTServer_polling_ms)

    # Flag set to True when CT is connected
    CT_is_connected = False
    
    # CT Server request received
    CTRequest = 0     
  
    # Try to connect to CTServer
    while not CT_is_connected:
        try:
            print("Try to connect...")
            CTServer_socket.connect((m_CTServer_ip, m_CTServer_port))

            # Send first Ack symbol to CT
            print("Send ACK symbol = ", m_CSServer_Ack_symbol.encode('utf-8'))
            CTServer_socket.sendall(m_CSServer_Ack_symbol.encode('utf-8'))
            
            # Now connected
            CT_is_connected = 1
            
            print("Successfully connect to CT server !")
            
        except TimeoutError:
            print("Fail to connect to CT server...")
        except ConnectionRefusedError:
            print("Trigger server refused the connection... Try again in 5s...")
            time.sleep(5)
        except ConnectionAbortedError:
            print("Trigger server aborted the connection... Try again in 5s...")
            time.sleep(5)
        except:
            print("Unexcpected error")           
  
    #####################################
    # POLLING PROCESS FOR CTServer request
    #####################################
    
    while 1:
        
        try:
            
            # Try to read data comming from CT Server
            CTRequest = CTServer_socket.recv(1024)
        
            # Cast in str
            CTRequest = CTRequest.decode()
            
            print("CT request is = " + CTRequest)
            
            # Send request to main process through pipe
            m_process_pipe.send(CTRequest)
            
            # Acknowledge CTServer
            CTServer_socket.sendall(m_CSServer_Ack_symbol.encode())

        except TimeoutError:
            print("Nothing from CT server ...")    
            pass