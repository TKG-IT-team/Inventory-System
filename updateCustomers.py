from Shopify.ShopifyCustomerAPI import ShopifyCustomerAPI
from Shopee import ShopeeAPI
from functions import API_KEY, PASSWORD, HOSTNAME, VERSION
from functions import CUSTOMER_DATA
from functions import combine_dfs


if __name__ == "__main__":

    ###Shopify
    print("Updating Shopify Customers...")
    shopify = ShopifyCustomerAPI(API_KEY, PASSWORD, HOSTNAME, VERSION).generate_full_cust_df()
    
    ###Shopee 
    print("Updating Shopee Customers...")
    shopee = ShopeeAPI.generate_full_cust_df()

    #Combine df
    combined = combine_dfs(shopify, shopee)

    #Export as excel
    combined.to_excel(CUSTOMER_DATA, index=False)