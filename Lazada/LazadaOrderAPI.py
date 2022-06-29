from lazop_sdk import LazopClient, LazopRequest
import sys
import os
# setting path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import config_tools_lazada as config_tools
import pandas as pd
from LazadaAuthorisation import Authorisation

import sys
import os
# setting path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from functions import convert_ISO, generate_qty_table


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
    #orders.to_excel("lazada_raw2.xlsx", index=False)
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
    df = pd.DataFrame(response.body['data'])
    df['order_id'] = order_id
    return df

#Get order more detail, like address, remark
def get_order_details2(order_id):
    access_token = get_new_access_token()

    url = f"https://api.lazada.sg/rest"
    app_key, app_secret = config_tools.read_credentials_config()

    client = LazopClient(url, app_key ,app_secret)
    request = LazopRequest('/order/get','GET')
    request.add_api_param('order_id', order_id) 
    response = client.execute(request, access_token)
    df = pd.DataFrame(response.body['data']['address_billing'], index=[0])
    df['address'] = df['address1'] + " " + df['post_code']
    df['Notes'] = response.body['data']['remarks']
    df['order_id'] = order_id
    return df

#Cleans data in the dataframe
def clean_df(df):
  
    df = df[['order_id', 'created_at',  'status', 'Notes', 'paid_price', 'currency', 'name' , 'phone', 'address', 'first_name']] # keep needed columns

    df = df.rename(columns={"order_id":"Order No.", "created_at":"Created At","status":"Fulfillment Status", "remark":"Notes",  #Renames columns
    "phone":"HP", "address":"Address", "first_name":"Name", "paid_price":"Amount Spent", "currency":"Currency","name":"Product" })

    df["Product"] = "{'" + df["Product"].values + "':1}"
    df["Platform"] = "Lazada"

    df = df.reset_index(drop=True)

    return df

#Splits one column into individual columns
def split_column(df, column_header):
    new_df = pd.DataFrame()
    for dictItr in df[column_header]: #split item_list into individual columns
        temp_df = pd.DataFrame.from_dict([dictItr])
        new_df = pd.concat([temp_df,new_df])
    return new_df

#Generate full order df
def generate_full_order_df(defaultQtyDf):
    df = get_all_orders()
    df = clean_df(df)
    df, unmatchedProducts = generate_qty_table(df, defaultQtyDf)
    return df, unmatchedProducts

def get_all_orders():
    order_list_df = get_order_list()

    df = pd.DataFrame() #empty dataframe
    
    #loops through every order id in order list dataframe and gets order detail
    for order_id in order_list_df["order_id"]:
        order_df = get_order_details(order_id)
        order_df2 = get_order_details2(order_id)
        order_df = pd.merge(order_df, order_df2, on='order_id', how='left')
        df = pd.concat([df,order_df])
    #df = pd.merge(df, order_list_df[['order_id', 'address_billing']], on='order_id', how='left')
    #splits address_billing into individual columns
    #address_df = split_column(df, "address_billing")
    #address_df['order_id'] = df['order_id'].values
    #df = pd.merge(df, address_df, on='order_id', how='left')
    return df
    
#clean_df(get_all_orders()).to_excel("test.xlsx", index=False)
