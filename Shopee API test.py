import hmac
import time
import requests
import hashlib
import json


class ShopeeAPI:
    def __init__(self):
        self.test_host = "https://partner.test-stable.shopeemobile.com"
        self.live_host = "https://partner.shopeemobile.com"
        self.v2_path = "/api/v2/shop/auth_partner"
        self.v1_path = "/api/v1/shop/auth_partner"
        self.redirect_url = "https://www.google.com/"
        self.test_partner_id = 1007820
        self.live_partner_id = 2004004
        self.test_partner_key = "67d8de39ffeb50042e95d7277e09670d470248e1200762598237accc1849810b"
        self.live_partner_key = "44799f965c4c2d99ef73fcbadc6fea88f8879c06f3d560b7f31c04f9cc8b030d"
        self.shop_id = 2421911
    
    def cal_token(redirect_url, partner_key): #V1
        base_string = partner_key + redirect_url
        token = hashlib.sha256(base_string.encode(encoding = 'UTF-8')).hexdigest()     # note: not HMAC
        return token
    
    def generateAuthorisationUrl1(self): #V1
        token = self.cal_token(self.redirect_url, self.live_partner_key)
        url = f"{self.live_host}{self.v1_path}?id={self.live_partner_id}&token={token}&redirect={self.redirect_url}"
        return url

    def generateAuthorisationUrl2(self): #V2
        timest = int(time.time())
        base_string = "%s%s%s"%(self.live_partner_id, self.v2_path, timest)
        sign = hmac.new(self.live_partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
        
        url = self.live_host + self.v2_path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s"%(self.live_partner_id,timest,sign,self.redirect_url)
        return url
    
    #Get token for shop level
    def get_token_shop_level(self, code, partner_id, partner_key, shop_id): #v2
        timest = int(time.time())
        body = {"code": code, "shop_id": shop_id, "partner_id": partner_id}
        host = "https://partner.shopeemobile.com"
        path = "/api/v2/auth/token/get"
        base_string = "%s%s%s"%(partner_id, path, timest)
        sign = hmac.new(str(partner_key).encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
        url = host + path + "?partner_id=%s&timestamp=%s&sign=%s"%(partner_id, timest, sign)

        headers = { "Content-Type": "application/json"}
        resp = requests.post(url, json=body, headers=headers)
        ret = json.loads(resp.content)
        access_token = ret.get("access_token")
        new_refresh_token = ret.get("refresh_token")
        return access_token, new_refresh_token, sign

    #Get token for account level 
    def get_token_account_level(self, code, partner_id, partner_key, main_account_id): #v2
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
    
    # Get order list
    def getOrderList(self): #Get new customers after the existing newest customer ID in database
        # while True:
        time_range_field = "create_time"
        time_from = 1610391652
        time_to = 1611687652
        page_size = 20

        url = f"{self.live_host}/api/v2/order/get_order_list?time_range_field={time_range_field}&time_from={time_from}&time_to={time_to}&page_size={page_size}"

        response = requests.request("GET", url)
        print(response.content)
            # df=pd.DataFrame(response.json()['customers'])
            # customers=pd.concat([customers,df])
            # last=df['id'].iloc[-1]
        #     if len(response.content)<15:
        #         break
        # return(response.content) 
    def test(self):
        #access_token, new_refresh_token, sign = self.get_token_shop_level(self.redirect_url, self.live_partner_id, self.live_partner_key, self.shop_id)
        access_token, new_refresh_token, sign = self.get_token_shop_level(self.redirect_url, self.live_partner_id, self.live_partner_key, self.shop_id)
        print(access_token)
        print(sign)


ShopeeAPI().test()
print(int(time.time()))
