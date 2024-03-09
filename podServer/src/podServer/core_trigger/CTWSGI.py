import socket

"""
    IP address and port of the core_trigger server. Could not be changed, as core_trigger server
    is on the same device and will always accept connection to 127.0.0.1 for WSGI adapter
"""
CT_SERVER_IP = "127.0.0.1"
CT_SERVER_PORT = 1205

"""
    REGISTERED request that will be pass to core_trigger server.
    Received requests not in this list will be ommited
"""
LAUNCHER_PCK = {'auth_key': "",
                'pck_rq' : "",
                'pck_key' : ""}

"""
    Authorized key to send data
"""
AUTH_KEY = "GillietBeynard!"

def get_auth_key():
    return LAUNCHER_PCK['auth_key']


def build_CT_packet():
    return (LAUNCHER_PCK['pck_rq'] + ":" + LAUNCHER_PCK['pck_key']).encode('utf-8')

"""
    Function called by the wsgi_adapter.py
"""
def run(environ, start_response):
    
    data_valid = False
    output = ""
    
    # Parse incoming request
    if 'QUERY_STRING' in environ.keys():
        if len(environ['QUERY_STRING']) > 1:
            # Get request raw data
            raw_request = str(environ['QUERY_STRING'])
            # Extract variables
            request_variables = raw_request.split('&')
            
            # Iterate through variables received by HTTP, and keep only the registered one  
            for http_variable in request_variables:
                # Divide variable name from value
                http_var, http_var_value = http_variable.split('=')
                # If variable name is registered, save the value
                if http_var in LAUNCHER_PCK.keys():
                    # Save variable value
                    LAUNCHER_PCK[http_var] = http_var_value
                    # State that new variables must be passed to core_trigger
                    data_valid = True

    # Check if key is right to authorized variable transfer to core_trigger
    if get_auth_key() != AUTH_KEY:
        output = b'KEY ERROR'
    else:    

        # If new variables were received (and thus must be passed to trigger_core)
        if data_valid:      
            
            # Create socket to connect to main server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((CT_SERVER_IP, CT_SERVER_PORT))
        
            # Format and send data to core_trigger
            client_socket.sendall(build_CT_packet())
            
            # Receive max 1024 bytes from core_trigger server connected
            output = client_socket.recv(1024)
            
            # Close socket before returning
            client_socket.close()
            
            
        else:
            
            output = b'No update'
        
        status = '200 OK'
    
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    
    start_response(status, response_headers)
    
    return [output]
