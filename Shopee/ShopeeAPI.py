import hmac
import time
import requests
import hashlib
import json
import pandas as pd

from datetime import datetime
import sys
import os
import pathlib
# setting path
# sys.path.append(os.path.abspath(os.path.join(pathlib.Path.cwd(), '..')))
sys.path.append(os.path.abspath(pathlib.Path.cwd()))
import Shopee.config_tools_shopee as config_tools


from functions import combine_dfs, generate_qty_table, convert_epoch, get_default_qty, logger
import ctypes

host = "https://partner.shopeemobile.com"
v2_path = "/api/v2/shop/auth_partner"
redirect_url = "https://www.google.com/"
partner_id = 2004004
partner_key = "44799f965c4c2d99ef73fcbadc6fea88f8879c06f3d560b7f31c04f9cc8b030d"
shop_id = 2421911
shop_test_id = 52362
access_token = ""
sign = ""

#Generates an authorisation url for a code that lasts 1 year
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
    timest = int(time.time())
    path = "/api/v2/auth/access_token/get"
    body = {"shop_id": shop_id, "refresh_token": refresh_token, "partner_id": partner_id}

    base_string = "%s%s%s"%(partner_id, path, timest)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s"%(partner_id, timest, sign)

    headers = { "Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    ret = json.loads(resp.content)
    access_token = ret.get("access_token")
    new_refresh_token = ret.get("refresh_token")
    return access_token, new_refresh_token
    
#Gets order list
def get_order_list(access_token, time_from, time_to):
    timest = int(time.time())
    path = "/api/v2/order/get_order_list"
    base_string = "%s%s%s%s%s"%(partner_id, path, timest, access_token, shop_id)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
  
    time_range_field = "create_time"
    page_size = 20

    payload={}
    headers = {

    }

    url = f"{host}{path}?timestamp={timest}&time_range_field={time_range_field}&sign={sign}&access_token={access_token}&shop_id={shop_id}&time_from={time_from}&time_to={time_to}&page_size={page_size}&partner_id={partner_id}"
    response = requests.request("GET", url)
    dictResponse = json.loads(response.content)
    listOrder = dictResponse['response']['order_list']
    newListOrder = []
    for order in listOrder:
        newListOrder.append(order['order_sn'])
    strListOrder="".join(elem + "," for elem in newListOrder)
    return strListOrder

#Gets the detail of the order   
def get_order_detail(access_token, order_sn_list):
    timest = int(time.time())
    path = "/api/v2/order/get_order_detail"
    base_string = "%s%s%s%s%s"%(partner_id, path, timest, access_token, shop_id)
    sign = hmac.new(partner_key.encode(encoding = 'UTF-8', errors = 'strict'), base_string.encode(encoding = 'UTF-8', errors = 'strict'), hashlib.sha256).hexdigest()
  
    response_optional_fields = "item_list,recipient_address"
    payload={}
    headers = {

    }
    
    url = f"{host}{path}?timestamp={timest}&response_optional_fields={response_optional_fields}&order_sn_list={order_sn_list}&sign={sign}&access_token={access_token}&shop_id={shop_id}&partner_id={partner_id}"
    try:
        response = requests.request("GET", url)
        dictResponse = json.loads(response.content.decode())
        listOrder = dictResponse['response']['order_list']
        df = pd.DataFrame() #empty dataframe
        for order in listOrder: #split item_list into individual columns
            order_df = pd.DataFrame.from_dict([order])
            dictItem = {}
            for item in order["item_list"]:
                dictItem[item["item_name"]]  =  item["model_quantity_purchased"]
            order_df["Product"] = str(dictItem)
            repi_df = pd.DataFrame(order_df['recipient_address'][0], index=[0])
            repi_df.drop(['region'], axis=1, inplace=True)
            order_df = order_df.join(repi_df)
            df = pd.concat([df,order_df])
    except ConnectionError as connection_error:
        error_msg = "Shopee API: Connection error while getting order details! Please refer to the error log for more information."
        print(error_msg)
        logger.error(f"Lazada API: Connection error while getting order details! \n{connection_error}")
        ctypes.windll.user32.MessageBoxW(0,error_msg, "Error Message", 0)
        df = pd.DataFrame()
    return df

#Gets the orders from shopee and convert it to an excel file
#Returns all orders by default
def get_orders(last_date = 1577808000): # by deafult, from 2020-1-1 to now, step: 15 days
    access_token, refresh_token = config_tools.readConfig()
    if (len(refresh_token) == 0):
        critical_msg = f"Please get code from authorization using the URL: \n{generateAuthorisationUrl2()}"
        print(critical_msg)
        logger.critical(critical_msg) 
        ctypes.windll.user32.MessageBoxW(0, f"Shopee API: {critical_msg}", "Error Message", 0)
        access_token, refresh_token = get_token_shop_level("4957526567585762414c586b4c494567")
    else:
        access_token, refresh_token = refresh_token_shop_level(refresh_token)
    print("Shopee:")
    print("refresh token: " + refresh_token)
    print ("access_token: " + access_token)
    print("\n")
    config_tools.writeConfig(access_token, refresh_token)
    df = pd.DataFrame() #empty dataframe
    for i in range(last_date, int(datetime.timestamp(datetime.now())), 1296000): 
        str_order_list = get_order_list(access_token, i, i + 1296000)
        if len(str_order_list) > 0:
            df = pd.concat([df,get_order_detail(access_token, str_order_list)])
    return df

#Cleans data in the dataframe
def clean_df(df):
    df.drop(['cod', 'days_to_ship', 'reverse_shipping_fee', 'update_time', 'region', 'ship_by_date'], axis=1, inplace=True) #Removes unused columns
    df = df.rename(columns={"create_time":"Created At", "order_sn":"Order No.","order_status":"Fulfillment Status", #Renames columns
    "message_to_seller":"Notes","currency":"Currency","item_name":"Product", "name":"Name", "phone":"HP",
    "full_address":"Address", })
    df["Created At"]  = df["Created At"].apply(datetime.fromtimestamp)#Changes timestamp to datetime
    df = df.reindex(columns=["Order No.", "Created At", "Fulfillment Status", "Notes", "Address", "Name", "Product", "Platform"]) #Reorder Columns, "recipient_address"
    
    #Add platform name to dataframe
    df["Platform"] = "Shopee"
    df = df.reset_index(drop=True)

    #Sort by date
    df = df.sort_values(by="Created At")
 
    return df

#Remove customer data from cleaned data
def clean_wo_customer_data(old_df, new_df):
    #check old df is correct, use left join instead
    new_df = new_df.reset_index(drop=True)
    old_df = old_df.reset_index(drop=True)
    new_df.drop(['HP', 'Address', 'Name'], axis=1, inplace=True)
    new_df = new_df.merge(old_df[['Order No.', 'HP', 'Address', 'Name']], how="left", on="Order No.")
    new_df = new_df.reset_index(drop=True)
    
    return new_df

#Generate full order df
def generate_full_order_df(defaultQtyDf):
    df = get_orders()
    df = clean_df(df)
    #df, unmatchedProducts = generate_qty_table(df, defaultQtyDf, "Shopee")
    return df

#Returns a dataframe of orders since last input date
def generate_new_order_df(default_qty_df, lastDate, old_df=pd.DataFrame()): #lastDate in IS08601 format
    epoch_date = convert_epoch(lastDate)
    new_df = get_orders(epoch_date)

    if len(new_df)!=0: #If there are new orders since last_date
        new_df = clean_df(new_df)
        # if len(old_df) != 0: #If there are any orders from outdated database to update
        #     trimmed_df = new_df[new_df["Created At"] <= old_df["Created At"].iloc[-1]]
        #     updated_old_df = clean_wo_customer_data(old_df, trimmed_df)
        #     new_df = combine_dfs(updated_old_df, new_df[new_df["Created At"] > old_df["Created At"].iloc[-1]])
        #df, unmatched_products = generate_qty_table(new_df, default_qty_df, "Shopee")
        return new_df
    else:
        unmatched_products = pd.Series(dtype=str)
        return new_df

#Returns a datafram of all uncensored customer information
def generate_full_cust_df():
    default_qty = get_default_qty()
    orders = generate_full_order_df(default_qty)
    # orders = pd.read_excel("orders.xlsx")
    boolean_list = []
    for i, order in orders.iterrows():
        if ("*" not in order["Name"] and 
            "*" not in order["Address"]):
            boolean_list.append(True)
        else:
            boolean_list.append(False)
    cust_df = orders.loc[boolean_list, ["Name", "HP", "Address"]]
    cust_df["Platform"] = "Shopee"
    return cust_df

# cust_df = generate_full_cust_df()
# cust_df.to_excel("Test.xlsx", index=False)
# print(generateAuthorisationUrl2())
# get_all_orders()

# from functions import get_default_path, get_default_qty
# get_default_path()
# defaultQtyDf = get_default_qty()

# #For Lazada
# generate_full_order_df(defaultQtyDf)
