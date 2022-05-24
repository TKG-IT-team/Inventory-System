import pandas as pd
from datetime import datetime
from ShopifyCustomerAPI import ShopifyCustomerAPI
import ShopifyOrderAPI
import json

#Shopify
apiKey = "1da062b3aea0f3a1a3eed35d52510c20"
password = "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" #CONFIDENTIAL
hostname = "TheKettleGourmet.myshopify.com"
version = "2022-04"

currTime = str(datetime.now())
formattedCurrTime = currTime[:9] + "T" + currTime[11:18]

#Combines dataframes
def combineDfs(*args): #Takes in pandas dataframe
    listOfDfs = []
    for arg in args:
        listOfDfs.append(arg)

    combinedDf = listOfDfs[0]
    for idx in range(len(listOfDfs) - 1):
        combinedDf.append(list[idx + 1])

    return combinedDf

#Use given column value as keys and rest of column values in list as values
def colAsKeys(df, colName):
    result = df.set_index(colName).T.to_dict('list')
    return result

#Combines dataframes of both customers and orders
def combineOrdersCustDf(customerDf, orderDf):
    custNameKeyDf = colAsKeys(customerDf, "Customer_id")

    #Combining Order and Customer DF
    for index, series in orderDf.iterrows():
        if series["Customer_id"] in custNameKeyDf.keys():
            orderDf.at[index, "HP"] = custNameKeyDf[series["Customer_id"]][0]
            orderDf.at[index, "Address"] = custNameKeyDf[series["Customer_id"]][1]
            orderDf.at[index, "Birthday"] = custNameKeyDf[series["Customer_id"]][2]
            orderDf.at[index, "Email"] = custNameKeyDf[series["Customer_id"]][3]
        else:
            print(series["name"] + " Not Found in Customer Data")

    return orderDf #Combined Order and Customer DF
                

#Returns the default qty in pandas Dataframe
#Note: Default quantity Excel File MUST be within the same directory 
def getDefaultQty(): 
    defaultQtyDf = pd.read_excel("setting.xlsx")
    return defaultQtyDf

if __name__ == "__main__":
    ###Shopify
    #Get customers database
    ShopifyFullCustDf = ShopifyCustomerAPI(apiKey, password, hostname, version).generateFullCustDf()
    ShopifyFullCustDf.to_excel(r"Customer Data.xlsx", index=False)

    #Get orders database
    defaultQtyDf = getDefaultQty()
    ShopifyFullOrderDf, unmatchedProducts = ShopifyOrderAPI.generateFullOrderDf(defaultQtyDf)
    ShopifyFullOrderDf.to_excel(r"Order Data.xlsx", index=False)
    
    #Combine Customer and Order Df
    shopifyCombined = combineOrdersCustDf(ShopifyFullCustDf, ShopifyFullOrderDf)

    #Combining platforms
    combinedDf = combineDfs(shopifyCombined)
    combinedDf.to_excel(r"Combined Data.xlsx", index=False)

    #Updating Inventory
