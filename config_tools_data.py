import configparser
import os
import pathlib

#Reads dictionary of path from config
def readConfig():

    # Create object
    config_file = configparser.ConfigParser()

    # Read config file
    config_file.read(str(pathlib.Path.cwd()) + '/' + "configurations.ini")

    return config_file["Path"]

