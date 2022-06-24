import configparser
import os

#Writes access_token and refresh_token onto config
def write_token_config(access_token, refresh_token):
    
    # Create object
    config_file = configparser.ConfigParser()

    # Add section
    config_file.add_section("Token")
    config_file.add_section("Credentials")

    # Add setting to section
    config_file.set("Token", "access_token", access_token)
    config_file.set("Token", "refresh_token", refresh_token)

    #Keep credentials
    app_key, app_secret = read_credentials_config()
    config_file.set("Credentials", "app_key", app_key)
    config_file.set("Credentials", "app_secret", app_secret)

    # Save config file
    with open(os.path.dirname(__file__) + '/' + "configurations.ini", 'w') as configfileObj:
        config_file.write(configfileObj)
        configfileObj.flush()
        configfileObj.close()


#Reads access_token and refresh_token from config
def read_token_config():

    # Create object
    config_file = configparser.ConfigParser()

    # Read config file
    config_file.read(os.path.dirname(__file__) + '/' + "configurations.ini")

    return config_file["Token"]["access_token"], config_file["Token"]["refresh_token"]


#Reads access_token and refresh_token from config
def read_credentials_config():

    # Create object
    config_file = configparser.ConfigParser()

    # Read config file
    config_file.read(os.path.dirname(__file__) + '/' + "configurations.ini")

    return config_file["Credentials"]["app_key"], config_file["Credentials"]["app_secret"]

