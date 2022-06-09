import pandas as pd
from datetime import datetime
import ShopifyOrderAPI
import dateutil.parser as parser
import os

import credentials

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

def convertISO(date):
    date = parser.parse(date)
    convertedDate = date.isoformat()
    return convertedDate

def getLatestDate(combinedOrderDf):
    listOfDates = []
    platformCount = []
    currPlatform = combinedOrderDf["Platform"].iloc[0]
    for i, series in combinedOrderDf.iterrows():
        if i != len(combinedOrderDf) - 1:
            if combinedOrderDf["Platform"].iloc[i + 1] == currPlatform and currPlatform not in platformCount:
                if series["Fulfillment Status"] == "unfulfilled":
                    listOfDates.append(series["Created At"])
                    platformCount.append(currPlatform)
            elif combinedOrderDf["Platform"].iloc[i+1]!=currPlatform and currPlatform not in platformCount:
                listOfDates.append(series["Created At"])
                currPlatform = combinedOrderDf["Platform"].iloc[i + 1]
            else:
                currPlatform = combinedOrderDf["Platform"].iloc[i+1]
        elif currPlatform not in platformCount:
            listOfDates.append(series["Created At"])
    return listOfDates


if __name__ == "__main__":

    #Gets path setting
    getDefaultPath()
    
    #Get default quantities
    defaultQtyDf = getDefaultQty() 
    
    #Gets customer database
    shopifyFullCustDf = pd.read_excel(customerData)

    #Gets old orders database
    oldCombinedOrderDf = pd.read_excel(combinedData)
    listOfDates = getLatestDate(oldCombinedOrderDf)
    print(convertISO(listOfDates[0]))

    ###Shopify
    shopifyNewOrderDf, unmatchedProducts = ShopifyOrderAPI.generateNewOrderDf(defaultQtyDf, convertISO(listOfDates[0]))
    # shopifyNewOrderDf.to_excel(r"C:\Users\zychi\OneDrive - National University of Singapore\The Kettle Gourmet Internship\Github\New Order.xlsx", index=False)

    #Combines Customer and Order Df
    shopifyCombined = combineOrdersCustDf(shopifyFullCustDf, shopifyNewOrderDf)
    shopifyCombined.to_excel("Test_new_combined_data.xlsx", index=False)
    #Combines platforms
    newCombinedOrderDf = combineDfs(shopifyCombined)

    #Combines with old CombinedOrderDf
    # newCombinedOrderDf.to_excel("Test_new_combined_data.xlsx", index=False)
    oldCombinedOrderDf.to_excel("Test_old_combined_data.xlsx", index=False)
    updatedCombinedDf = combineDfs(oldCombinedOrderDf, newCombinedOrderDf)
    updatedCombinedDf.to_excel("Test_combined_data.xlsx", index=False)
    # updatedCombinedDf.to_excel(r"C:\Users\zychi\OneDrive - National University of Singapore\The Kettle Gourmet Internship\Github\New Combined Order.xlsx", index=False)

