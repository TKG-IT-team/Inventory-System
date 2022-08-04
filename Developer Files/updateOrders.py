import pandas as pd
from Shopify import ShopifyOrderAPI
from Shopee import ShopeeAPI
import Lazada.LazadaOrderAPI as LazadaOrderAPI
from functions import get_default_path, get_default_qty, combine_orders_cust_df, combine_dfs, convert_ISO, add_one_sec_ISO

FINAL_FULFILLMENT_STATUS = ["fulfilled", "CANCELLED", "COMPLETED", "canceled", "delivered", "returned", "lost_by_3pl", "damaged_by_3pl"]

#Split df into multiple platforms based on dates, returns a list of Dfs
def split_platforms(combined_order_df):
    platform_order_dfs = {}
    lastIndex = 0
    for i in range(len(combined_order_df)):
        if i != len(combined_order_df) - 1:
            if combined_order_df["Platform"].iloc[i] != combined_order_df["Platform"].iloc[i + 1]:
                platform_order_dfs[combined_order_df["Platform"].iloc[i]] = combined_order_df.iloc[lastIndex:i + 1, : ]
                lastIndex = i + 1
        else:
            platform_order_dfs[combined_order_df["Platform"].iloc[i]] = combined_order_df.iloc[lastIndex: , : ]
    return platform_order_dfs

#Get Latest Date
def get_update_date(order_df):
    for i, series in order_df.iterrows():
        if series["Fulfillment Status"] not in FINAL_FULFILLMENT_STATUS:
            return series["Created At"]
   
    return add_one_sec_ISO(order_df["Created At"].iloc[-1])

#Split dataframe after a given date
def split_df_based_on_date(order_df, date): #Given date must be in ISO format
    order_df = order_df.reset_index(drop=True)
    for i, series in order_df.iterrows():
        if convert_ISO(series["Created At"]) >= date:
            return order_df.iloc[ : i, : ], order_df.iloc[i : , : ]
    return order_df, pd.DataFrame(columns=order_df.columns.tolist())

#Adds new rows to dataframe if it does not exist
def add_new_row_df(old_df, new_df, str_key_col):
    combined_df = old_df
    new_df = new_df.reset_index(drop=True)
    for i, series in new_df.iterrows():
        if (not series[str_key_col] in combined_df[str_key_col].values) and (not str(series[str_key_col]) in combined_df[str_key_col].values):
            combined_df = pd.concat([combined_df, new_df.iloc[[i]]])
    combined_df[str_key_col] = combined_df[str_key_col].astype(str)
    combined_df = combined_df.sort_values(by=str_key_col)
    return combined_df

#Update fullfilled status
def update_fullfilled_status(old_df, new_df, str_key_col, str_fullfill_col):
     update_df = old_df
     super_new_df = pd.DataFrame(new_df)
     super_new_df.set_index(str_key_col, inplace=True)
     update_df = update_df.reset_index(drop=True)
     for i, series in update_df.iterrows():
         if series[str_key_col] in super_new_df.index:
             if series[str_fullfill_col] != super_new_df.at[series[str_key_col], str_fullfill_col]:
                 update_df.at[i,str_fullfill_col] = super_new_df.at[series[str_key_col], str_fullfill_col]
     return update_df

if __name__ == "__main__":

    #Gets path setting
    COMBINED_DATA = get_default_path()
    
    #Gets customer database
    # shopify_full_cust_df = pd.read_excel(CUSTOMER_DATA)

    #Gets old orders database
    oldCombined = pd.read_excel(COMBINED_DATA)
    platformDict = split_platforms(oldCombined)
    date_dict = {}
    for platform, df in platformDict.items():
        date = get_update_date(df)
        print(str(platform) + " : " + str(date)) 
        converted_date = convert_ISO(date)
        date_dict[platform] = converted_date

    #empty dataframe
    updated_shopify = pd.DataFrame()
    updated_shopee = pd.DataFrame()
    updated_lazada = pd.DataFrame()
    
    # ###Shopify
    if "Shopify" in platformDict.keys():
        print("Updating Shopify orders...")
        shopify_new_order_df = ShopifyOrderAPI.generate_new_order_df(date_dict["Shopify"])

        updated_shopify = shopify_new_order_df
        
        # #Combines Customer and Order Df
        # new_shopify = combine_orders_cust_df(shopify_full_cust_df, shopify_new_order_df)
        
        #Combines old and new Shopify Df
        #split = split_df_based_on_date(platformDict["Shopify"], date_dict["Shopify"])
        #old_shopify = split[0]
        #updated_shopify = combine_dfs(old_shopify, shopify_new_order_df)
    else:
        updated_shopify = ShopifyOrderAPI.generate_full_order_df()
        
    if "Shopee" in platformDict.keys():
        ###Shopee
        print("Updating Shopee orders...")
        split = split_df_based_on_date(platformDict["Shopee"], date_dict["Shopee"])
        new_shopee = ShopeeAPI.generate_new_order_df(date_dict["Shopee"], split[1])
        updated_shopee = new_shopee
        #Combines old and new Shopify Df
        #old_shopee = split[0]
        #updated_shopee = combine_dfs(old_shopee, new_shopee)
    else:
        updated_shopee = ShopeeAPI.generate_full_order_df()

    if "Lazada" in platformDict.keys():
        ##Lazada
        print("Updating Lazada orders...")
        split = split_df_based_on_date(platformDict["Lazada"], date_dict["Lazada"])
        new_lazada = LazadaOrderAPI.generate_new_order_df(date_dict["Lazada"], split[1])

        updated_lazada = new_lazada
        #Combines old and new lazada Df
        #old_lazada = split[0]
        #updated_lazada = combine_dfs(old_lazada, new_lazada)
    else:
        updated_lazada = LazadaOrderAPI.generate_full_order_df()

    #Combines platforms
    newCombined = combine_dfs(updated_shopify, updated_shopee, updated_lazada)
    #Add new rows to oldCombined if does not exist
    final_df = oldCombined
    if len(newCombined) > 0:
        final_df = update_fullfilled_status(oldCombined, newCombined, r'Order No.', 'Fulfillment Status')
        final_df = add_new_row_df(final_df, newCombined, 'Order No.')
    final_df.to_excel(COMBINED_DATA,index=False)
