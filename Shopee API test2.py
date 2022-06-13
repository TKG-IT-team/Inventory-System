import hmac
import time
import requests
import hashlib
import json
import configparser

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

def readConfig():

    # CREATE OBJECT
    config_file = configparser.ConfigParser()

    # READ CONFIG FILE
    config_file.read("configurations.ini")

    return config_file["Token"]["access_token"], config_file["Token"]["refresh_token"]

test_host = "https://partner.test-stable.shopeemobile.com"
live_host = "https://partner.shopeemobile.com"
v2_path = "/api/v2/shop/auth_partner"
v1_path = "/api/v1/shop/auth_partner"
redirect_url = "https://www.google.com/"
test_partner_id = 1007820
live_partner_id = 2004004
test_partner_key = "67d8de39ffeb50042e95d7277e09670d470248e1200762598237accc1849810b"
live_partner_key = "44799f965c4c2d99ef73fcbadc6fea88f8879c06f3d560b7f31c04f9cc8b030d"
shop_id = 2421911
shop_test_id = 52362
access_token = ""
sign = ""

def cal_token(redirect_url, partner_key): #V1
    base_string = partner_key + redirect_url
    token = hashlib.sha256(base_string.encode(encoding = 'UTF-8')).hexdigest()     # note: not HMAC
    return token
    
def generateAuthorisationUrl1(): #V1
    token = self.cal_token(redirect_url, live_partner_key)
    url = f"{self.live_host}{self.v1_path}?id={self.live_partner_id}&token={token}&redirect={self.redirect_url}"
    return url

def generateAuthorisationUrl2(): #V2
    timest = int(time.time())
    base_string = "%s%s%s"%(test_partner_id, v2_path, timest)
    sign = hmac.new(test_partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
        
    url = test_host + v2_path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s"%(test_partner_id,timest,sign,redirect_url)
    return url
    

#Gets token for shop level
def get_token_shop_level(code, partner_id, partner_key, shop_id): #v2
    timest = int(time.time())
    body = {"code": code, "shop_id": shop_id, "partner_id": partner_id}
    host = test_host
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
def refresh_token_shop_level(refresh_token,partner_id, partner_key, shop_id): #v2
    print("refresh token")
    timest = int(time.time())
    host = test_host
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
    host = test_host
    path = "/api/v2/order/get_order_list"
    base_string = "%s%s%s%s%s"%(test_partner_id, path, timest, access_token, shop_test_id)
    sign = hmac.new(test_partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
  
    time_range_field = "create_time"
    time_from = 1610391652
    time_to = 1611687652
    page_size = 20

    payload={}
    headers = {

    }

    url = f"{test_host}/api/v2/order/get_order_list?timestamp={timest}&time_range_field={time_range_field}&sign={sign}&access_token={access_token}&shop_id={shop_test_id}&time_from={time_from}&time_to={time_to}&page_size={page_size}&partner_id={test_partner_id}"

    response = requests.request("GET", url)
    print(response.content)
            # df=pd.DataFrame(response.json()['customers'])
            # customers=pd.concat([customers,df])
            # last=df['id'].iloc[-1]
        #     if len(response.content)<15:
        #         break
        # return(response.content) 
def test():
    access_token, refresh_token = readConfig()
    if (len(refresh_token) == 0):
        print("Please get token from authorization")
        access_token, refresh_token = get_token_shop_level("6261625a504879506a427a75784a6e6c", test_partner_id, test_partner_key, shop_test_id)
    else:
        access_token, refresh_token = refresh_token_shop_level(refresh_token, test_partner_id, test_partner_key, shop_test_id)
    writeConfig(access_token, refresh_token)
    print("refresh token: " + refresh_token)
    print ("access_token: " + access_token)
    getOrderList(access_token)

print(generateAuthorisationUrl2())
# test()
#ShopeeAPI().getOrderList()

#print(int(time.time()))

