## 1. API data extraction

from wsgiref.simple_server import demo_app
from numpy import true_divide
import requests
import pandas as pd
import ast
from datetime import datetime
import dateutil.parser as parser

#Converts pandas dataframe series to dictionary
def convertSeriesToDict(series):
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

def convertISO(date):
    date = parser.parse(date)
    convertedDate = date.isoformat()
    return convertedDate

#Get new orders
def get_new_orders(lastDate): #lastDate in ISO 8601 format
    last = lastDate
    orders=pd.DataFrame()
    # while True:
    url = f"https://1da062b3aea0f3a1a3eed35d52510c20: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@TheKettleGourmet.myshopify.com/admin/api/2022-04/orders.json?limit=250&fulfillment_status=any&status=any&updated_at_min={last}"
    
    response = requests.request("GET", url)
    df=pd.DataFrame(response.json()['orders'])
    print(df['created_at'].iloc[0])
    orders=pd.concat([orders,df])
    last=convertISO(df['created_at'].iloc[0])
        
        # if len(df)<250:
        #     break
    return(orders)

shopifyNewOrderDf = get_new_orders("2021-05-10T12:56:37")
shopifyNewOrderDf.to_excel("Test_new_combined_data.xlsx", index=False)

def add_to_dictProduct(dictProduct, output):
    if 'product_id' in dictProduct.keys():
        product_name = dictProduct['product_id']
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

    # Mutates columns
    # df['order_number'] = 'S' + df['order_number'].astype(str)
    df['created_at'] = df['created_at'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %I:%M:%S %p'))
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
        dataRow = convertSeriesToDict(series)
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
        dataRow = convertSeriesToDict(series)
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
        dataRow = convertSeriesToDict(series)
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
        dataRow = convertSeriesToDict(series)
        dataRow = dataRow["line_items"]
        if str(type(dataRow)) != "<class 'list'>":
            df.at[i, "product"] = str(dictProduct)
            continue
        for j in range(len(dataRow)):
            if str(type(dataRow[j])) == "<class 'list'>":
                for z in range(len(dataRow[j])):
                    dictProduct = add_to_dictProduct(dataRow[j][z] , dictProduct)
            else:
                dictProduct = add_to_dictProduct(dataRow[j], dictProduct)
        df.at[i, "product"] = str(dictProduct)

    df.drop('line_items', axis=1, inplace=True)

    #Drop rows with financial status = refunded or voided
    for i, series in df.iterrows():
        print(series["order_number"] + series["financial_status"])
        if series["financial_status"] == "refunded" or series["financial_status"] == "voided":
            df.drop(index=i, axis=0)

    return df

def getDefaultQty(): 
    defaultQtyDf = pd.read_excel("Product Setting.xlsx")
    return defaultQtyDf

def generateFullOrderDf(defaultQtyDf):
    df = pd.DataFrame(get_all_orders())
    df = clean(df)
    unmatchedProducts = []
    PLATFORM = 'Shopify'
    platform = []
    for i, orderSeries in df.iterrows():
        orderStr = orderSeries["product"]
        orderDict = ast.literal_eval(orderStr)
        platform.append(PLATFORM)
        pdtComponents = {}
        for product_id, qty in orderDict.items():
            if (product_id in defaultQtyDf["id"].tolist()):
                for flavour in defaultQtyDf.columns:
                    if flavour not in pdtComponents.keys():
                        pdtComponents[flavour] = qty * defaultQtyDf.at[defaultQtyDf[defaultQtyDf["id"]==product_id].index.values[0], flavour]
                    else:
                        pdtComponents[flavour] += qty * defaultQtyDf.at[defaultQtyDf[defaultQtyDf["id"]==product_id].index.values[0], flavour]
            else:
                if len(unmatchedProducts) == 0:
                    unmatchedProducts.append(product_id)
                elif product_id not in unmatchedProducts:
                    unmatchedProducts.append(product_id)
                else:
                    pass
        for component, componentQty in pdtComponents.items():
            df.at[i,component] = componentQty
    
    df["Platform"] = platform
    if len(unmatchedProducts) > 0:
        print("Unmatched Products: " + str(unmatchedProducts))
        # messagebox.showinfo("Unmatched Products", "There are unmatched products. Please check Settings to verify all product inputs.")

    return df, pd.Series(unmatchedProducts, name = "Unmatched Products")


#Returns a dataframe of orders since last input date
def generateNewOrderDf(defaultQtyDf, lastDate): #lastDate in ISO 8601 format
    df = get_new_orders(lastDate)
    df = clean(df)
    unmatchedProducts = []
    PLATFORM = 'Shopify'
    platform = []
    for i, orderSeries in df.iterrows():
        orderStr = orderSeries["product"]
        orderDict = ast.literal_eval(orderStr)
        platform.append(PLATFORM)
        pdtComponents = {}
        for product_id, qty in orderDict.items():
            if (product_id in defaultQtyDf["id"].tolist()):
                for flavour in defaultQtyDf.columns:
                    if flavour not in pdtComponents.keys():
                        pdtComponents[flavour] = qty * defaultQtyDf.at[defaultQtyDf[defaultQtyDf["id"]==product_id].index.values[0], flavour]
                    else:
                        pdtComponents[flavour] += qty * defaultQtyDf.at[defaultQtyDf[defaultQtyDf["id"]==product_id].index.values[0], flavour]
            else:
                if len(unmatchedProducts) == 0:
                    unmatchedProducts.append(product_id)
                elif product_id not in unmatchedProducts:
                    unmatchedProducts.append(product_id)
                else:
                    pass
        for component, componentQty in pdtComponents.items():
            df.at[i,component] = componentQty
    
    df["Platform"] = platform
    if len(unmatchedProducts) > 0:
        print("Unmatched Products: " + str(unmatchedProducts))
        # messagebox.showinfo("Unmatched Products", "There are unmatched products. Please check Settings to verify all product inputs.")

    return df, pd.Series(unmatchedProducts, name = "Unmatched Products")