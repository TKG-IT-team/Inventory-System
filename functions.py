import pandas as pd
import os
import dateutil.parser as parser
import ast
import config_tools_data

#Shopify
API_KEY = "1da062b3aea0f3a1a3eed35d52510c20"
PASSWORD = "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" #CONFIDENTIAL
HOSTNAME = "TheKettleGourmet.myshopify.com"
VERSION = "2022-04"

#Column Names
COL_CUSTOMER_ID = "Customer_id"
COL_HP = "HP"
COL_ADDRESS = "Address"
COL_BIRTHDAY = "Birthday"
COL_EMAIL = "Email"

#FilePath
PATH_SETTING_FP = os.path.dirname(os.path.realpath(__file__)) + "\Path Setting.xlsx"
SETTING_FP = os.path.dirname(os.path.realpath(__file__)) +  "\Product Setting.xlsx"
CUSTOMER_DATA = os.path.dirname(os.path.realpath(__file__)) + "\Customer Data.xlsx"
COMBINED_DATA = os.path.dirname(os.path.realpath(__file__)) + "\Combined Data.xlsx"

#Combines dataframes
def combine_dfs(*args): #Takes in pandas dataframe
    combinedDf = pd.DataFrame()
    for arg in args:
        combinedDf = pd.concat([combinedDf, arg])

    return combinedDf

#Use given column value as keys and rest of column values in list as values
def col_as_keys(df, colName):
    result = df.set_index(colName).T.to_dict('list')
    return result

#Combines dataframes of both customers and orders
def combine_orders_cust_df(customerDf, orderDf):
    custNameKeyDf = col_as_keys(customerDf, COL_CUSTOMER_ID)

    #Combining Order and Customer DF
    for index, series in orderDf.iterrows():
        if series[COL_CUSTOMER_ID] in custNameKeyDf.keys():
            orderDf.at[index, COL_HP] = custNameKeyDf[series[COL_CUSTOMER_ID]][1]
            orderDf.at[index, COL_ADDRESS] = custNameKeyDf[series[COL_CUSTOMER_ID]][3]
            orderDf.at[index, COL_BIRTHDAY] = custNameKeyDf[series[COL_CUSTOMER_ID]][2]
            orderDf.at[index, COL_EMAIL] = custNameKeyDf[series[COL_CUSTOMER_ID]][4]
        else:
            print(series["Name"] + " Not Found in Customer Data")
    
    #Drop customer_id col
    orderDf.drop([COL_CUSTOMER_ID],axis=1,inplace=True)

    #Reordering columns
    cols = orderDf.columns.tolist()
    cols = cols[0:4] + cols[-4:] + cols[4:-4]
    orderDf = orderDf[cols]

    return orderDf #Combined Order and Customer DF
                

#Returns the default qty in pandas Dataframe
#Note: Default quantity Excel File MUST be within the same directory 
def get_default_qty(): 
    defaultQtyDf = pd.read_excel(SETTING_FP)
    return defaultQtyDf

#Returns the default path for setting
def get_default_path():
    
    dictPath = config_tools_data.readConfig()
   
    global settingFP
    global customerData
    global combinedData
    SETTING_FP = dictPath["SettingFilePath"]
    CUSTOMER_DATA = dictPath["CustomerDataFilePath"]
    COMBINED_DATA = dictPath["CombinedDataFilePath"]

#Generate quantity table based on the product dictionary
def generate_qty_table(df, defaultQtyDf):
    unmatchedProducts = []
    for i, orderSeries in df.iterrows():
        orderStr = orderSeries["Product"]
        orderDict = ast.literal_eval(orderStr)
        pdtComponents = {}
        for product_name, qty in orderDict.items():
            if (product_name in defaultQtyDf["title"].tolist()):
                for flavour in defaultQtyDf.columns.tolist()[2:]:
                    if flavour not in pdtComponents.keys():
                        pdtComponents[flavour] = qty * defaultQtyDf.at[defaultQtyDf[defaultQtyDf["title"]==product_name].index.values[0], flavour]
                    else:
                        pdtComponents[flavour] += qty * defaultQtyDf.at[defaultQtyDf[defaultQtyDf["title"]==product_name].index.values[0], flavour]
            else:
                if len(unmatchedProducts) == 0:
                    unmatchedProducts.append(product_name)
                elif product_name not in unmatchedProducts:
                    unmatchedProducts.append(product_name)
                else:
                    pass
        for component, componentQty in pdtComponents.items():
            df.at[i,component] = componentQty
    

    if len(unmatchedProducts) > 0:
        print("Unmatched Products: " + str(unmatchedProducts))
        # messagebox.showinfo("Unmatched Products", "There are unmatched products. Please check Settings to verify all product inputs.")

    return df, pd.Series(unmatchedProducts, name = "Unmatched Products")

#Converts date to ISO8601 format
def convert_ISO(date):
    date = parser.parse(date)
    convertedDate = date.isoformat()
    return convertedDate

#Converts date from ISO to epoch format
def convert_epoch(date):
    date = parser.isoparse(date).timestamp()
    return date
