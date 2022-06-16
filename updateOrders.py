import pandas as pd
from datetime import datetime
from Shopify import ShopifyOrderAPI
import dateutil.parser as parser
import os

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
    combinedDf = pd.DataFrame()
    for arg in args:
        combinedDf = pd.concat([combinedDf, arg])
        # combinedDf = combinedDf.concat(list[id  x + 1])

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
    defaultPathDF = pd.read_excel(pathSettingFP, index_col = 0)
    global settingFP
    global customerData
    global combinedData
    settingFP =  defaultPathDF.at["SettingFilePath", "Path"]
    customerData =  defaultPathDF.at["CustomerDataFilePath", "Path"]
    combinedData = defaultPathDF.at["CombinedDataFilePath", "Path"]


#Converts date to ISO8601 format
def convertISO(date):
    date = parser.parse(date)
    convertedDate = date.isoformat()
    return convertedDate


#Split df into multiple platforms based on dates, returns a list of Dfs
def splitPlatforms(combinedOrderDf):
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
def getLatestDate(orderDf):
    for i, series in orderDf.iterrows():
        if series["Fulfillment Status"] == "unfulfilled":
            return series["Created At"]
    return orderDf["Created At"].iloc[-1]

#Remove rows after a given date
def removeRowsAfterDate(orderDf, date): #Given date must be in ISO format
    for i, series in orderDf.iterrows():
        if convertISO(series["Created At"]) > date:
            return orderDf.iloc[0 : i - 1, : ]
    return orderDf

if __name__ == "__main__":

    #Gets path setting
    getDefaultPath()
    
    #Get default quantities
    defaultQtyDf = getDefaultQty() 
    
    #Gets customer database
    shopifyFullCustDf = pd.read_excel(customerData)

    #Gets old orders database
    oldCombined = pd.read_excel(combinedData)
    
    platformDict = splitPlatforms(oldCombined)
    dateDict = {}
    for platform, df in platformDict.items():
        date = getLatestDate(df)
        convertedDate = convertISO(date)
        dateDict[platform] = convertedDate


    ###Shopify
    shopifyNewOrderDf, unmatchedProducts = ShopifyOrderAPI.generateNewOrderDf(defaultQtyDf, dateDict["Shopify"])

    #Combines Customer and Order Df
    newShopify = combineOrdersCustDf(shopifyFullCustDf, shopifyNewOrderDf)
    
    #Combines old and new Shopify Df
    oldShopify = removeRowsAfterDate(platformDict["Shopify"], dateDict["Shopify"])
    updatedShopify = combineDfs(oldShopify, newShopify)

    #Combines platforms
    newCombined = combineDfs(updatedShopify)
    newCombined.to_excel(combinedData, index=False)

