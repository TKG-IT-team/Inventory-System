from Shopify.ShopifyCustomerAPI import ShopifyCustomerAPI
import Shopify.ShopifyOrderAPI as ShopifyOrderAPI
from functions import get_default_path, get_default_qty, combine_orders_cust_df, combine_dfs
from functions import API_KEY, PASSWORD, HOSTNAME, VERSION #For Shopify
from functions import CUSTOMER_DATA, COMBINED_DATA
    
if __name__ == "__main__":

    #Gets path setting
    get_default_path()

    ###Shopify
    #Gets customers database
    ShopifyFullCustDf = ShopifyCustomerAPI(API_KEY, PASSWORD, HOSTNAME, VERSION).generate_full_cust_df()
    ShopifyFullCustDf.to_excel(CUSTOMER_DATA, index=False)

    #Gets orders database
    defaultQtyDf = get_default_qty()
    ShopifyFullOrderDf, unmatchedProducts = ShopifyOrderAPI.generate_full_order_df(defaultQtyDf)

    #Combines Customer and Order Df
    shopifyCombined = combine_orders_cust_df(ShopifyFullCustDf, ShopifyFullOrderDf)

    #Combines platforms
    combinedDf = combine_dfs(shopifyCombined)
    combinedDf.to_excel(COMBINED_DATA, index=False)
