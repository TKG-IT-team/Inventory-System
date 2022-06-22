## 1. API data extraction
from wsgiref.simple_server import demo_app
import requests
import pandas as pd
from datetime import datetime, timedelta
import dateutil.parser as parser
from functions import generate_qty_table

#Converts pandas dataframe series to dictionary
def convert_series_to_dict(series):
    diction = series.to_dict()
    return diction

#Get all orders
def get_all_orders():
    last=0
    orders=pd.DataFrame()
    while True:
        url = f"https://1da062b3aea0f3a1a3eed35d52510c20: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@TheKettleGourmet.myshopify.com/admin/api/2022-04/orders.json?limit=250&fulfillment_status=any&status=any&since_id={last}"
        #?limit=250&fulfillment_status=any&status=any&since_id={last}
    
        response = requests.request("GET", url)

        df=pd.DataFrame(response.json()['orders'])
        orders=pd.concat([orders,df])
        last=df['id'].iloc[-1]
        if len(df)<250:
            break
    return(orders)

#Minus 8 hours
def convert_ISOGMT(date):
    date = parser.parse(date) + timedelta(hours=-8)
    convertedDate = date.isoformat()
    return convertedDate

#Get new orders
def get_new_orders(last_date): #lastDate in ISO 8601 format
    last_date = convert_ISOGMT(last_date)
    orders=pd.DataFrame()
    lastId = 0
    while True:
        url = f"https://1da062b3aea0f3a1a3eed35d52510c20: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@TheKettleGourmet.myshopify.com/admin/api/2022-04/orders.json?limit=250&fulfillment_status=any&status=any&created_at_min={last_date}&since_id={lastId}"
        #?limit=250&fulfillment_status=any&status=any&since_id={last}

        response = requests.request("GET", url)

        df=pd.DataFrame(response.json()['orders'])
        orders=pd.concat([orders,df])
        lastId = df['id'].iloc[-1]
        if len(df)<250:
            break
    return(orders)

  
def add_to_dict_product(dictProduct, output):
    if "title" in dictProduct.keys():
        product_name = dictProduct["title"]
        qty = dictProduct['quantity']
        if not product_name in output.keys():
            output[product_name] = qty
        else:
            currQty = output[product_name]
            output[product_name] = currQty + qty
    return output

## 2. Cleaning of data - orders
def clean(df):
    # Keeps the columns we need
    df = df[['order_number','created_at' ,'financial_status' , 'fulfillment_status', 'note', 'customer', 'line_items', 'total_price_set', 'shipping_address']]

    # Mutates columns (change date format)

    df = df.assign(created_at=[datetime.strptime(x, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %I:%M:%S %p') for x in df.created_at])
    
    df = df.reset_index(drop=True)
    #Change fulfillment status to fulfilled for orders in 2021 and before
    for i, series in df.iterrows():    
        if series["fulfillment_status"] == None:
            if series["created_at"].startswith(("2021","2020")):
                df.at[i, "fulfillment_status"] = "fulfilled"
            else:
                df.at[i, "fulfillment_status"] = "unfulfilled"

    #Gets the name from customer
    for i, series in df.iterrows():
        dataRow = convert_series_to_dict(series)
        dataRow = dataRow["customer"]
        if str(type(dataRow)) != "<class 'dict'>":
            df.at[i, "name"] = ""
            df.at[i, "Customer_id"] = ""
            continue
        if "default_address" in dataRow.keys():
            df.at[i, "name"] = dataRow["default_address"]["name"].lower()
            df.at[i, "Customer_id"] = dataRow["default_address"]["customer_id"]

    df.drop('customer', axis=1, inplace=True)

    #Gets the amount and currency from total_price_set
    df.reset_index() 
    for i, series in df.iterrows():
        dataRow = convert_series_to_dict(series)
        dataRow = dataRow["total_price_set"]
        amount = ""
        currency = ""   
        if (not pd.isna(dataRow)) and "shop_money" in dataRow.keys():
            amount = dataRow["shop_money"]["amount"]
            currency = dataRow["shop_money"]["currency_code"]
        df.at[i, "amount"] = amount
        df.at[i, "currency_code"] = currency
    df.drop('total_price_set', axis=1, inplace=True)

    #Gets the address from shipping_address
    for i, series in df.iterrows():
        dataRow = convert_series_to_dict(series)
        dataRow = dataRow["shipping_address"]
        address = ""
        if str(type(dataRow)) != "<class 'dict'>":
            df.at[i, "address1"] = address
            continue
        if (not pd.isna(dataRow)) and "address1" in dataRow.keys():
            address = dataRow["address1"]
            df.at[i, "address1"] = address.lower()
        if (not pd.isna(dataRow)) and "address2" in dataRow.keys():
            address = address + " " + str(dataRow["address2"])
            df.at[i, "address2"] = address.lower()
    df.drop('shipping_address', axis=1, inplace=True)

    #Gets the product from line_items
    df.reset_index() 
    for i, series in df.iterrows():
        dictProduct = {}
        dataRow = convert_series_to_dict(series)
        dataRow = dataRow["line_items"]
        if str(type(dataRow)) != "<class 'list'>":
            df.at[i, "product"] = str(dictProduct)
            continue
        for j in range(len(dataRow)):
            if str(type(dataRow[j])) == "<class 'list'>":
                for z in range(len(dataRow[j])):
                    dictProduct = add_to_dict_product (dataRow[j][z] , dictProduct)
            else:
                dictProduct = add_to_dict_product(dataRow[j], dictProduct)
        df.at[i, "product"] = str(dictProduct)

    df.drop('line_items', axis=1, inplace=True)

    
    #Drop rows with financial status = refunded or voided
    for i, series in df.iterrows():
        if series["financial_status"] == "refunded" or series["financial_status"] == "voided":
            df.drop(index=i, axis=0, inplace=True)

    #Add platform name to dataframe
    df["Platform"] = "Shopify"

    #Dropping unecessary columns and renaming them
    df.drop(['financial_status', 'address1', 'address2'],axis=1,inplace=True) #'product', 'id', 'Customer_id'
    df = df.rename(columns={'order_number': 'Order No.', 'created_at': 'Created At', 'note' : 'Notes', 'name': 'Name', 'currency_code': 'Currency', 'title': 'Product Orders', 'amount':'Amount Spent', 'fulfillment_status': "Fulfillment Status", "product": "Product"})

    return df

#Generate Full Order Df
def generate_full_order_df(default_qty_df):
    df = pd.DataFrame(get_all_orders())
    df = clean(df)
    df, unmatchedProducts = generate_qty_table(df, default_qty_df)
    return df, unmatchedProducts

#Returns a dataframe of orders since last input date
def generate_new_order_df(default_qty_df, last_date): #lastDate in ISO 8601 format
    df = get_new_orders(last_date)
    df = clean(df)
    df, unmatchedProducts = generate_qty_table(df, default_qty_df)
    return df, unmatchedProducts
