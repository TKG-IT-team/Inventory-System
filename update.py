
from datetime import datetime
from ShopifyCustomerAPI import ShopifyCustomerAPI
import ShopifyOrderAPI 
import pandas as pd

#Shopify
apiKey = "1da062b3aea0f3a1a3eed35d52510c20"
password = "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" #CONFIDENTIAL
hostname = "TheKettleGourmet.myshopify.com"
version = "2022-04"

currTime = str(datetime.now())
formattedCurrTime = currTime[:9] + "T" + currTime[11:18]

#Combine dataframes
def combineDfs(*args):
    listOfDfs = []
    for arg in args:
        listOfDfs.append(arg)

    combinedDf = listOfDfs[0]
    for idx in range(len(listOfDfs) - 1):
        combinedDf.append(list[idx + 1])

    return combinedDf

#Use given column value as keys and rest of column values in list as values
def colAsKeys(df, colName):
    result = df.set_index({colName}).T.to_dict('list')
    return result

#Combines dataframes of both customers and orders
def combineOrdersCustDf(customerDf, orderDf):
    custNameKeyDf = colAsKeys(customerDf, "Name")
    
    hps = []
    addresses = []
    birthdays = []
    emails = []

    for index, series in orderDf.iterrows():
        if series["name"] in custNameKeyDf.keys():
            hps.append(custNameKeyDf[series["name"]][1])
            addresses.append(custNameKeyDf[series["name"]][2])
            birthdays.append(custNameKeyDf[series["name"]][3])
            emails.append(custNameKeyDf[series["name"]][4])
        else:
            print(series["name"] + " Not Found in Customer Data")

    #Combining Order and Customer DF
    orderDf["Address"] = addresses
    orderDf["HP"] = hps
    orderDf["Birthday"] = birthdays
    orderDf["Email"] = emails

    return orderDf #Combined Order and Customer DF
                

#Returns the default qty in pandas Dataframe
#Note: Default quantity Excel File MUST be within the same directory 
def getDefaultQty(): 
    defaultQtyDf = pd.read_excel("setting.xlsx")
    convertedDf = colAsKeys(defaultQtyDf, "Flavours")
    return convertedDf

if __name__ == "__main__":
    ###Shopify
    #Updating customers database
    shopifyFullCustDf = ShopifyCustomerAPI(apiKey, password, hostname, version).generateFullCustList()
    
    #Updating orders database
    defaultQtyDf = getDefaultQty()
    shopifyNewOrderDf = ShopifyOrderAPI.generateNewOrderDf(defaultQtyDf)
    
    #Combine Customer and Order Df
    shopifyCombined = combineOrdersCustDf(shopifyFullCustDf, shopifyNewOrderDf)
    
    #Combining platforms
    combinedDf = combineDfs(shopifyCombined)
    combinedDf.to_excel(r"C:\Users\zychi\OneDrive - National University of Singapore\The Kettle Gourmet Internship\app\Combined Data.xlsx", index=False)

    #Updating Inventory