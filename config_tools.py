import configparser

#Reads dictionary of path from config
def readConfig():

    # Create object
    config_file = configparser.ConfigParser()

    # Read config file
    config_file.read("configurations.ini")

    return config_file["Path"]

