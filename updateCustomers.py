from Shopify.ShopifyCustomerAPI import ShopifyCustomerAPI


#Shopify
apiKey = "1da062b3aea0f3a1a3eed35d52510c20"
password = "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" #CONFIDENTIAL
hostname = "TheKettleGourmet.myshopify.com"
version = "2022-04"


#FilePath
customerData = "Customer Data.xlsx"


if __name__ == "__main__":

    ###Shopify
    #Gets customers database
    ShopifyFullCustDf = ShopifyCustomerAPI(apiKey, password, hostname, version).generateFullCustDf()
    ShopifyFullCustDf.to_excel(customerData, index=False)