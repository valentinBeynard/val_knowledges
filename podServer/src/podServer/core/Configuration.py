'''
Created on 2 sept. 2023

@author: Valentin BEYNARD
'''

class ConfigHandler():
    
    
    def __init__(self, m_config_path, m_config_dict):
        
        self.config_path = m_config_path
        self.config_dict = m_config_dict


    def getConf(self, m_conf_param):
        return self.config_dict.get(m_conf_param)

    def setConf(self, m_conf_param, m_value):
        
        if m_conf_param in self.config_dict.keys():
            self.config_dict[m_conf_param] = m_value
            return 0
        else:
            return -1

    def create_conf_file(self):
        
        try:
            # Create configuration file
            conf_file = open(self.config_path, 'w')
            
            # Write default configuration attributes
            for key, elem in self.config_dict.items():
                conf_file.write(key + "=" + elem + "\n")
            
            print("Configuration file created !")
            
            return conf_file
        except IOError:
            print("Error: Can't create configuration file !")
            return -1

    def initConf(self):
            # Load configuration
        try:
            conf_file = open(self.config_path, 'r')
        except IOError:
            print("Error: File does not appear to exist. Creating one")
            # Create configuration file
            conf_file = self.create_conf_file()
            
            # Assert fail
            if conf_file == -1:
                return -1
            
            # Close previous 'w' opened file
            conf_file.close()
            
            # Open configuration file freshly created in 'r' mode
            conf_file = open(self.config_path, 'r')     
        
        # Parse configuration
        for line in conf_file:
            # Remove end line character
            line = line[:-1]
            # Divide key and element
            line = line.split('=')
            
            # Find if exist in configuration
            if line[0] in self.config_dict.keys():
                self.setConf(line[0], line[1])
            else:
                print("Error: Bad configuration line !")   


if __name__ == '__main__':
    pass