import hmac
import time
import requests
import hashlib
import json

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
    

#Get token for shop level
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

#Get token for account level 
def get_token_account_level(code, partner_id, partner_key, main_account_id): #v2
    timest = int(time.time())
    body = {"code": code, "main_account_id": main_account_id, "partner_id": partner_id}
    host = test_host
    path = "/api/v2/auth.token/get"
    base_string = "%s%s%s"%(partner_id, path, timest)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s"%(partner_id, timest, sign)
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    ret = json.loads(resp.content)
    access_token = ret.get("access_token")
    new_refresh_token = ret.get("refresh_token")
    return access_token, new_refresh_token, sign
    
# Get order list
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
    #access_token, new_refresh_token, sign = self.get_token_shop_level(self.redirect_url, self.live_partner_id, self.live_partner_key, self.shop_id)
    access_token, new_refresh_token = get_token_shop_level("63565356684849516e727153737a4e65", test_partner_id, test_partner_key, shop_test_id)
    getOrderList(access_token)
   
    
def test2():
    
    url = "https://partner.test-stable.shopeemobile.com/api/v2/order/get_order_list?access_token=524c536f7178665259584876774d4443&order_status=%22READY_TO_SHIP%22&page_size=20&partner_id=1007820&response_optional_fields=%22order_status%22&shop_id=52362&sign=sign&time_from=1607235072&time_range_field=%22create_time%22&time_to=1608271872&timestamp=timestamp"
  
    payload={}
    headers = {

    }
    response = requests.request("GET",url,headers=headers, data=payload, allow_redirects=False)

    print(response.text)

#print(generateAuthorisationUrl2())
test()
#ShopeeAPI().getOrderList()
#test2()

#print(int(time.time()))
