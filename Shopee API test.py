import hmac
import time
import requests
import hashlib
import json

timest = int(time.time())
test_host = "https://partner.test-stable.shopeemobile.com"
host = "https://partner.shopeemobile.com"
path = "/api/v2/shop/auth_partner"
redirect_url = "https://www.google.com/"
partner_id = 1007820
partner_key = "67d8de39ffeb50042e95d7277e09670d470248e1200762598237accc1849810b"
base_string = "%s%s%s"%(partner_id, path, timest)
sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()

####generate api
url = host + path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s"%(partner_id,timest,sign,redirect_url)
print(url)



class ShopeeOrderAPI:
    def __init__(self):
        pass
    
    # Get order list
    def getOrderList(self): #Get new customers after the existing newest customer ID in database
        # while True:
        time_range_field = "create_time"
        time_from = 1610391652
        time_to = 1611687652
        page_size = 20

        url = f"{host}/api/v2/order/get_order_list?time_range_field={time_range_field}&time_from={time_from}&time_to={time_to}&page_size={page_size}"

        response = requests.request("GET", url)
        print(response.content)
            # df=pd.DataFrame(response.json()['customers'])
            # customers=pd.concat([customers,df])
            # last=df['id'].iloc[-1]
        #     if len(response.content)<15:
        #         break
        # return(response.content) 

# ShopeeOrderAPI().getOrderList()

# def cal_token(redirect_url, partner_key):
#     base_string = partner_key + redirect_url
#     token = hashlib.sha256(base_string.encode(encoding = 'UTF-8')).hexdigest()     # note: not HMAC
#     return token

# print(cal_token(redirect_url, partner_key))

# order_path = "/api/v2/order/get_order_list"
# access_token, new_refresh_token = get_token_shop_level()
# order_status = "READY_TO_SHIP"
# page_size = 20
# shop_id = 
# sign = 
# time_range_field = "create_time"
# url = (host + order_path + "?access_token=" + access_token + "&cursor=%22%22&order_status=" + order_status +
#      "&page_size=" + page_size + "&partner_id=" + partner_id + "&shop_id=" + shop_id + "&sign=" + sign + 
#      "&time_from=1607235072&time_range_field=" + time_range_field + "&time_to=1608271872&timestamp=" + timest


def get_token_shop_level(code, partner_id, partner_key, shop_id):
    timest = int(time.time())
    body = {"code": code, "shop_id": shop_id, "partner_id": partner_id}
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/auth/token/get"
    base_string = "%s%s%s"%(partner_id, path, timest)
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s"%(partner_id, timest, sign)

    headers = { "Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    ret = json.loads(resp.content)
    access_token = ret.get("access_token")
    new_refresh_token = ret.get("refresh_token")
    return access_token, new_refresh_token



def get_token_account_level(code, partner_id, partner_key, main_account_id):
    timest = int(time.time())
    body = {"code": code, "main_account_id": main_account_id, "partner_id": partner_id}
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/auth.token/get"
    base_string = "%s%s%s"%(partner_id, path, timest)
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    url = host + path + "?partnet_id=%s%timestamp=%s&sign=%s"%(partner_id, timest, sign)

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    ret = json.loads(resp.content)
    access_token = ret.get("access_token")
    new_refresh_token = ret.get("refresh_token")
    return access_token, new_refresh_token
