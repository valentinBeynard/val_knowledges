import socket

TRIGGER_SERVER_IP = "127.0.0.1"
TRIGGER_SERVER_PORT = 1205
CONFIG_PATH = ""

LAUNCHER_PCK = {'rq' : "",
                'key' : ""}

def get_request():
    return LAUNCHER_PCK.get('rq')

def application(environ, start_response):
    
    print("HTTP request !")
    request_id = "EMPTY"
    
    # Parse incoming request
    if 'QUERY_STRING' in environ.keys():
        if len(environ['QUERY_STRING']) > 1:
            # Get request raw data
            raw_request = str(environ['QUERY_STRING'])
            # Extract variables
            request_variables = raw_request.split('&')
            
            # Parse variables
            for http_variable in request_variables:
                http_var, http_var_value = http_variable.split('=')
                if http_var in LAUNCHER_PCK.keys():
                    LAUNCHER_PCK[http_var] = http_var_value

    if get_request() == 'CMD_LAUNCH':      
        # Create socket to connect to main server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((TRIGGER_SERVER_IP, TRIGGER_SERVER_PORT))
    
        # Send ON signal
        client_socket.sendall(b'CMD_LAUNCH')
        
        # Close socket before returning
        client_socket.close()
        
        output = b'CMD_LAUNCH!'
        
    else:
        
        output = b'Hello World: ' + request_id.encode()
    
    status = '200 OK'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    

    
    return [output]