import pandas as pd
from Shopify import ShopifyOrderAPI
from Shopee import ShopeeAPI
from functions import get_default_path, get_default_qty, combine_orders_cust_df, combine_dfs, convert_ISO
from functions import CUSTOMER_DATA, COMBINED_DATA


UNFULFILLED_STATUS = ["unfulfilled", "TO_CONFIRM_RECEIVE", "PROCESSED"]

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
def get_latest_date(order_df):
    for i, series in order_df.iterrows():
        if series["Fulfillment Status"] in UNFULFILLED_STATUS:
            return series["Created At"]
    return order_df["Created At"].iloc[-1]

#Split dataframe after a given date
def split_df_based_on_date(order_df, date): #Given date must be in ISO format
    order_df = order_df.reset_index(drop=True)
    for i, series in order_df.iterrows():
        if convert_ISO(series["Created At"]) > date:
            return order_df.iloc[0 : i - 1, : ], order_df.iloc[i : , : ]
    return order_df, pd.DataFrame()

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


    # ###Shopify
    shopify_new_order_df, unmatched_products = ShopifyOrderAPI.generate_new_order_df(defaultQtyDf, date_dict["Shopify"])

    #Combines Customer and Order Df
    new_shopify = combine_orders_cust_df(shopify_full_cust_df, shopify_new_order_df)
    
    #Combines old and new Shopify Df
    split = split_df_based_on_date(platformDict["Shopify"], date_dict["Shopify"])
    old_shopify = split[0]
    old_shopify.to_excel("old.xlsx", index=False)
    new_shopify.to_excel("new.xlsx", index=False)
    updated_shopify = combine_dfs(old_shopify, new_shopify)

    ###Shopee
    split = split_df_based_on_date(platformDict["Shopee"], date_dict["Shopee"])
    new_shopee, unmatched_products = ShopeeAPI.generate_new_order_df(defaultQtyDf, date_dict["Shopee"], split[1])

    #Combines old and new Shopify Df
    old_shopee = split[0]
    updated_shopee = combine_dfs(old_shopee, new_shopee)

    #Combines platforms
    newCombined = combine_dfs(updated_shopify, updated_shopee)
    newCombined.to_excel(COMBINED_DATA, index=False)

