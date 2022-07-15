from Shopify.ShopifyCustomerAPI import ShopifyCustomerAPI
import Shopify.ShopifyOrderAPI as ShopifyOrderAPI
import Shopee.ShopeeAPI as ShopeeAPI
import Lazada.LazadaOrderAPI as LazadaOrderAPI
from functions import get_default_path, get_default_qty, combine_orders_cust_df, combine_dfs, convert_ISO
from functions import API_KEY, PASSWORD, HOSTNAME, VERSION
from functions import logger
import config_tools_data
import sys

def get_since_date():
    dictPath = config_tools_data.readConfig()
    since_date = dictPath["SinceDate"]

    try:
        if len(since_date) != 0:
            converted_date = convert_ISO(since_date)
            return converted_date
        else:
            return since_date
    except AttributeError:
        critical_msg = "Please enter since date in correct format!"
        print(critical_msg)
        logger.critical(critical_msg)
        sys.exit()
    
if __name__ == "__main__":
    
    #Gets path setting and since date
    CUSTOMER_DATA, COMBINED_DATA = get_default_path()

    # Gets customers database
    #print("Getting customers from Shopify...")
    #shopify_full_cust_df = ShopifyCustomerAPI(API_KEY, PASSWORD, HOSTNAME, VERSION).generate_full_cust_df()
    #shopify_full_cust_df.to_excel(CUSTOMER_DATA, index=False)

    #Gets orders database
    default_qty_df = get_default_qty()
    since_date = get_since_date()

    if len(since_date) == 0:
        #For Shopify
        print("Getting orders from Shopify...")
        shopify_full_order_df, unmatched_products = ShopifyOrderAPI.generate_full_order_df(default_qty_df)
        #For Shopee
        print("Getting orders from Shopee...")
        shopee_full_order_df, unmatched_products = ShopeeAPI.generate_full_order_df(default_qty_df)
        #For Lazada
        print("Getting orders from Lazada...")
        lazada_full_order_df, unmatched_products = LazadaOrderAPI.generate_full_order_df(default_qty_df)
    else:
        #For Shopify
        print(f"Getting orders from Shopify since {since_date}...")
        shopify_full_order_df, unmatched_products = ShopifyOrderAPI.generate_new_order_df(default_qty_df, since_date)
        #For Shopee
        print(f"Getting orders from Shopee since {since_date}...")
        shopee_full_order_df , unmatched_products = ShopeeAPI.generate_new_order_df(default_qty_df, since_date)
        #For Lazada
        print(f"Getting orders from Lazada since {since_date}...")
        lazada_full_order_df, unmatched_products = LazadaOrderAPI.generate_new_order_df(default_qty_df, since_date)

    #Combines Customer and Order Df
    #shopifyCombined = combine_orders_cust_df(shopify_full_cust_df, shopify_full_order_df)
    
    #Combines platforms
    combinedDf = combine_dfs(shopify_full_order_df, shopee_full_order_df, lazada_full_order_df) 
    combinedDf.to_excel(COMBINED_DATA, index=False)
