import configparser

#Writes access_token and refresh_token onto config
def writeConfig(access_token, refresh_token):
    
    # Create object
    config_file = configparser.ConfigParser()

    # Add section
    config_file.add_section("Token")

    # Add setting to section
    config_file.set("Token", "access_token", access_token)
    config_file.set("Token", "refresh_token", refresh_token)

    # Save config file
    with open(r"Shopee/configurations.ini", 'w') as configfileObj:
        config_file.write(configfileObj)
        configfileObj.flush()
        configfileObj.close()

#Reads access_token and refresh_token from config
def readConfig():

    # Create object
    config_file = configparser.ConfigParser()

    # Read config file
    config_file.read(r"Shopee/configurations.ini")
    print(config_file.sections())
    return config_file["Token"]["access_token"], config_file["Token"]["refresh_token"]

