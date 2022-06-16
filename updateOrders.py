import pandas as pd
from datetime import datetime
from Shopify import ShopifyOrderAPI
import dateutil.parser as parser
from functions import get_default_path, get_default_qty, combine_orders_cust_df, combine_dfs, convert_ISO, convert_epoch
from functions import CUSTOMER_DATA, COMBINED_DATA
from Shopee import ShopeeAPI

#Split df into multiple platforms based on dates, returns a list of Dfs
def split_platforms(combinedOrderDf):
    platformOrderDfs = {}
    lastIndex = 0
    for i, series in combinedOrderDf.iterrows():
        if i != len(combinedOrderDf) - 1:
            if combinedOrderDf["Platform"].iloc[i] != combinedOrderDf["Platform"].iloc[i + 1]:
                platformOrderDfs[combinedOrderDf["Platform"].iloc[i]] = combinedOrderDf.iloc[lastIndex:i, : ]
                lastIndex = i + 1
        else:
            platformOrderDfs[combinedOrderDf["Platform"].iloc[i]] = combinedOrderDf.iloc[lastIndex: , : ]
    return platformOrderDfs

#Get Latest Date
def get_latest_date(orderDf):
    for i, series in orderDf.iterrows():
        if series["Fulfillment Status"] == "unfulfilled":
            return series["Created At"]
    return orderDf["Created At"].iloc[-1]

#Remove rows after a given date
def remove_rows_after_date(orderDf, date): #Given date must be in ISO format
    for i, series in orderDf.iterrows():
        if convert_ISO(series["Created At"]) > date:
            return orderDf.iloc[0 : i - 1, : ]
    return orderDf

if __name__ == "__main__":

    #Gets path setting
    get_default_path()
    
    #Get default quantities
    defaultQtyDf = get_default_qty() 
    
    #Gets customer database
    shopify_full_cust_df = pd.read_excel(CUSTOMER_DATA)

    #Gets old orders database
    oldCombined = pd.read_excel(COMBINED_DATA)
    
    platformDict = split_platforms(oldCombined)
    date_dict = {}
    for platform, df in platformDict.items():
        date = get_latest_date(df)
        converted_date = convert_ISO(date)
        date_dict[platform] = converted_date


    ###Shopify
    shopify_new_order_df, unmatched_products = ShopifyOrderAPI.generate_new_order_df(defaultQtyDf, date_dict["Shopify"])

    #Combines Customer and Order Df
    new_shopify = combine_orders_cust_df(shopify_full_cust_df, shopify_new_order_df)
    
    #Combines old and new Shopify Df
    old_shopify = remove_rows_after_date(platformDict["Shopify"], date_dict["Shopify"])
    updated_shopify = combine_dfs(old_shopify, new_shopify)

    ###Shopee
    new_shopee, unmatched_products = ShopeeAPI.generate_new_order_df(defaultQtyDf, convert_epoch(date_dict["Shopify"]))

    #Combines old and new Shopify Df
    old_shopee = remove_rows_after_date(platformDict["Shopee"], date_dict["Shopee"])
    updated_shopee = combine_dfs(old_shopee, new_shopee)

    #Combines platforms
    newCombined = combine_dfs(updated_shopify, updated_shopee)
    newCombined.to_excel(COMBINED_DATA, index=False)

