import hmac
import time
import requests
import hashlib
import json
import configparser

#Writes access_token and refresh_token onto config
def writeConfig(access_token, refresh_token):
    
    # CREATE OBJECT
    config_file = configparser.ConfigParser()

    # ADD SECTION
    config_file.add_section("Token")

    # ADD SETTINGS TO SECTION
    config_file.set("Token", "access_token", access_token)
    config_file.set("Token", "refresh_token", refresh_token)

    # SAVE CONFIG FILE
    with open(r"configurations.ini", 'w') as configfileObj:
        config_file.write(configfileObj)
        configfileObj.flush()
        configfileObj.close()

#Reads access_token and refresh_token from config
def readConfig():

    # CREATE OBJECT
    config_file = configparser.ConfigParser()

    # READ CONFIG FILE
    config_file.read("configurations.ini")

    return config_file["Token"]["access_token"], config_file["Token"]["refresh_token"]

host = "https://partner.shopeemobile.com"
v2_path = "/api/v2/shop/auth_partner"
redirect_url = "https://www.google.com/"
partner_id = 2004004
partner_key = "44799f965c4c2d99ef73fcbadc6fea88f8879c06f3d560b7f31c04f9cc8b030d"
shop_id = 2421911
shop_test_id = 52362
access_token = ""
sign = ""
    
def generateAuthorisationUrl2(): #V2
    timest = int(time.time())
    base_string = "%s%s%s"%(partner_id, v2_path, timest)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
        
    url = host + v2_path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s"%(partner_id,timest,sign,redirect_url)
    return url
    

#Gets token for shop level
def get_token_shop_level(code): #v2
    timest = int(time.time())
    body = {"code": code, "shop_id": shop_id, "partner_id": partner_id}
    path = "/api/v2/auth/token/get"
    base_string = "%s%s%s"%(partner_id, path, timest)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s"%(partner_id, timest, sign)

    headers = { "Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    ret = json.loads(resp.content)
    print(ret)
    access_token = ret.get("access_token")
    new_refresh_token = ret.get("refresh_token")
    return access_token, new_refresh_token

#Refreshes the token
def refresh_token_shop_level(refresh_token): #v2
    print("refresh token")
    timest = int(time.time())
    path = "/api/v2/auth/access_token/get"
    body = {"shop_id": shop_id, "refresh_token": refresh_token, "partner_id": partner_id}

    base_string = "%s%s%s"%(partner_id, path, timest)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s"%(partner_id, timest, sign)

    print(url)

    headers = { "Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    ret = json.loads(resp.content)
    print(ret)
    access_token = ret.get("access_token")
    new_refresh_token = ret.get("refresh_token")
    return access_token, new_refresh_token

    
# Gets order list
def getOrderList(access_token): #Get new customers after the existing newest customer ID in database
    # while True:
    timest = int(time.time())
    path = "/api/v2/order/get_order_list"
    base_string = "%s%s%s%s%s"%(partner_id, path, timest, access_token, shop_id)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
  
    time_range_field = "create_time"
    time_from = 1610391652
    time_to = 1611687652
    page_size = 20

    payload={}
    headers = {

    }

    url = f"{host}/api/v2/order/get_order_list?timestamp={timest}&time_range_field={time_range_field}&sign={sign}&access_token={access_token}&shop_id={shop_id}&time_from={time_from}&time_to={time_to}&page_size={page_size}&partner_id={partner_id}"

    response = requests.request("GET", url)
    print(response.content)
         
def test():
    access_token, refresh_token = readConfig()
    if (len(refresh_token) == 0):
        print("Please get code from authorization")
        access_token, refresh_token = get_token_shop_level("4b6a73647a437562495a6a4849526f61")
    else:
        access_token, refresh_token = refresh_token_shop_level(refresh_token)
    writeConfig(access_token, refresh_token)
    print("refresh token: " + refresh_token)
    print ("access_token: " + access_token)
    getOrderList(access_token)

#print(generateAuthorisationUrl2())
test()
#ShopeeAPI().getOrderList()

#print(int(time.time()))

