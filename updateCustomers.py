from Shopify.ShopifyCustomerAPI import ShopifyCustomerAPI
from functions import API_KEY, PASSWORD, HOSTNAME, VERSION
from functions import CUSTOMER_DATA


if __name__ == "__main__":

    ###Shopify
    #Gets customers database
    ShopifyFullCustDf = ShopifyCustomerAPI(API_KEY, PASSWORD, HOSTNAME, VERSION).generate_full_cust_df()
    ShopifyFullCustDf.to_excel(CUSTOMER_DATA, index=False)