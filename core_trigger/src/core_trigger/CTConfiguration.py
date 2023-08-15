'''
Created on 29 juil. 2023

@author: valbe
'''

CONFIG_PATH = "./trigger_server.conf"

CONFIGURATION_DICT = {"MAIN_SERVER_IP" : "192.168.1.1",
                      "MAIN_SERVER_PORT" : "1204",
                      "WSGI_ADAPTOR_PORT" : "1205",
                      "POLLING_TIME_MS" : "6000",
                      "LAUNCHER_FILE" : "launching.ts",
                      "ON_SIGNAL_PINOUT" : "4"}


def getConf(m_conf_param):
    return CONFIGURATION_DICT.get(m_conf_param)

def setConf(m_conf_param, m_value):
    
    if m_conf_param in CONFIGURATION_DICT.keys():
        CONFIGURATION_DICT[m_conf_param] = m_value
        return 0
    else:
        return -1

def create_conf_file():
    
    try:
        # Create configuration file
        conf_file = open(CONFIG_PATH, 'w')
        
        # Write default configuration attributes
        for key, elem in CONFIGURATION_DICT.items():
            conf_file.write(key + "=" + elem + "\n")
        
        print("Configuration file created !")
        
        return conf_file
    except IOError:
        print("Error: Can't create configuration file !")
        return -1

def initConf():
        # Load configuration
    try:
        conf_file = open(CONFIG_PATH, 'r')
    except IOError:
        print("Error: File does not appear to exist. Creating one")
        # Create configuration file
        conf_file = create_conf_file()
        
        # Assert fail
        if conf_file == -1:
            return -1
        
        # Close previous 'w' opened file
        conf_file.close()
        
        # Open configuration file freshly created in 'r' mode
        conf_file = open(CONFIG_PATH, 'r')     
    
    # Parse configuration
    for line in conf_file:
        # Divide key and element
        line = line.split('=')
        
        # Find if exist in configuration
        if line[0] in CONFIGURATION_DICT.keys():
            setConf(line[0], line[1])
        else:
            print("Error: Bad configuration line !")   
            
            
            