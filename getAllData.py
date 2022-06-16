import pandas as pd
from datetime import datetime
from Shopify.ShopifyCustomerAPI import ShopifyCustomerAPI
import Shopify.ShopifyOrderAPI as ShopifyOrderAPI
import json
import sys
import os
import config_tools_data

#Shopify
apiKey = "1da062b3aea0f3a1a3eed35d52510c20"
password = "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" #CONFIDENTIAL
hostname = "TheKettleGourmet.myshopify.com"
version = "2022-04"

#Column Names
colCustomerID = "Customer_id"
colHP = "HP"
colAddress = "Address"
colBirthday = "Birthday"
colEmail = "Email"

#FilePath
pathSettingFP = os.path.dirname(os.path.realpath(__file__)) + "\Path Setting.xlsx"
settingFP = "Product Setting.xlsx"
customerData = "Customer Data.xlsx"
combinedData = "Combined Data.xlsx"


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
    custNameKeyDf = colAsKeys(customerDf, colCustomerID)

    #Combining Order and Customer DF
    for index, series in orderDf.iterrows():
        if series[colCustomerID] in custNameKeyDf.keys():
            orderDf.at[index, colHP] = custNameKeyDf[series[colCustomerID]][1]
            orderDf.at[index, colAddress] = custNameKeyDf[series[colCustomerID]][3]
            orderDf.at[index, colBirthday] = custNameKeyDf[series[colCustomerID]][2]
            orderDf.at[index, colEmail] = custNameKeyDf[series[colCustomerID]][4]
        else:
            print(series["name"] + " Not Found in Customer Data")
        
    #Dropping unecessary columns, reordering columns (For Shopify)
    orderDf.drop(['financial_status', 'address1', 'address2', 'Customer_id', 'id'],axis=1,inplace=True) #'product'
    orderDf = orderDf.rename(columns={'order_number': 'Order No.', 'created_at': 'Created At', 'note' : 'Notes', 'name': 'Name', 'currency_code': 'Currency', 'title': 'Product Orders', 'amount':'Amount Spent', 'fulfillment_status': "Fulfillment Status"})
    cols = orderDf.columns.tolist()
    cols = cols[0:4] + cols[-4:] + cols[4:-4]
    orderDf = orderDf[cols]

    return orderDf #Combined Order and Customer DF
                

#Returns the default qty in pandas Dataframe
#Note: Default quantity Excel File MUST be within the same directory 
def getDefaultQty(): 
    defaultQtyDf = pd.read_excel(settingFP)
    return defaultQtyDf

#Returns the default path for setting
def getDefaultPath():
    
    dictPath = config_tools_data.readConfig()
   
    global settingFP
    global customerData
    global combinedData
    settingFP = dictPath["SettingFilePath"]
    customerData = dictPath["CustomerDataFilePath"]
    combinedData = dictPath["CombinedDataFilePath"]
    
if __name__ == "__main__":
    
    #Gets path setting
    getDefaultPath()

    ###Shopify
    #Gets customers database
    ShopifyFullCustDf = ShopifyCustomerAPI(apiKey, password, hostname, version).generateFullCustDf()
    ShopifyFullCustDf.to_excel(customerData, index=False)

    #Gets orders database
    defaultQtyDf = getDefaultQty()
    ShopifyFullOrderDf, unmatchedProducts = ShopifyOrderAPI.generateFullOrderDf(defaultQtyDf)

    #Combines Customer and Order Df
    shopifyCombined = combineOrdersCustDf(ShopifyFullCustDf, ShopifyFullOrderDf)

    #Combines platforms
    combinedDf = combineDfs(shopifyCombined)
    combinedDf.to_excel(combinedData, index=False)
