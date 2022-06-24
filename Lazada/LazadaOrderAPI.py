from lazop_sdk import LazopClient, LazopRequest
import config_tools_lazada as config_tools
import pandas as pd
from LazadaAuthorisation import Authorisation

import sys
import os
# setting path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from functions import convert_ISO

#Get new access token
def get_new_access_token():
    access_token, refresh_token = config_tools.read_token_config()
    if (len(refresh_token) == 0):
        auth_url = Authorisation().concatenate_authorization_url()
        print(f"Please get code from authorization using the URL:\n{auth_url}")
        
        CODE = "0_110194_P5OR9Z4G8j6ap5IoGCihVWsB44280"
        access_token, refresh_token = Authorisation().get_access_token(CODE)
    else:
        access_token, refresh_token = Authorisation().refresh_access_token(refresh_token)
    config_tools.write_token_config(access_token, refresh_token)
    print("refresh token: " + refresh_token)
    print ("access_token: " + access_token)
    print("\n")
    return access_token

#Get orders and their ID
def get_order_list():
    access_token = get_new_access_token()
    
    url = f"https://api.lazada.sg/rest"
    app_key, app_secret = config_tools.read_credentials_config()

    orders=pd.DataFrame()
    last_created_after = '2021-01-01T00:00:00+08:00' #No orders before this date
    is_first_loop = True
    while True:
        client = LazopClient(url, app_key ,app_secret)
        request = LazopRequest('/orders/get','GET')
        request.add_api_param('created_after', last_created_after) 
        request.add_api_param('limit', '100') #100 is the maximum number of orders per GET request
        response = client.execute(request, access_token)

        if is_first_loop:  #Starts with first row   
            df = pd.DataFrame([response.body['data']['orders'][0]])
            for i in range(len(response.body['data']['orders']) - 1):
                temp_df = pd.DataFrame([response.body['data']['orders'][i + 1]])
                df = pd.concat([df, temp_df]) #For the particular loop of GET request
            orders = pd.concat([orders, df])
        else: #Starts with second row because first row is duplicate of previous loop dataframe because of variable "last_created_after"
            df = pd.DataFrame([response.body['data']['orders'][1]])
            for i in range(len(response.body['data']['orders']) - 2):
                temp_df = pd.DataFrame([response.body['data']['orders'][i + 2]])
                df = pd.concat([df, temp_df]) #For the particular loop of GET request
            orders = pd.concat([orders, df])

        last_created_after = convert_ISO(df['created_at'].iloc[-1])
        is_first_loop = False
        if is_first_loop and len(df)<100:
            break
        if not is_first_loop and len(df) < 99:
            break
    # orders.to_excel("lazada_raw2.xlsx", index=False)
    return orders

#Get order details
def get_order_details(order_id):
    access_token = get_new_access_token()

    url = f"https://api.lazada.sg/rest"
    app_key, app_secret = config_tools.read_credentials_config()

    client = LazopClient(url, app_key ,app_secret)
    request = LazopRequest('/order/items/get','GET')
    request.add_api_param('order_id', order_id) 
    response = client.execute(request, access_token)

    order_details = pd.DataFrame([response.body['data'][0]])
    print(response.body['data'][0].keys())
    return order_details

def get_product_details(product_id):
    
    return 0

if __name__ == "__main__":
    get_order_details(50220464779738)