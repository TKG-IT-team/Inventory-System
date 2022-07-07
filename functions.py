import pandas as pd
import os
import dateutil.parser as parser
import ast
import config_tools_data
from datetime import timedelta

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
def col_as_keys(df, col_name):
    result = df.set_index(col_name).T.to_dict('list')
    return result

#Combines dataframes of both customers and orders
def combine_orders_cust_df(customerDf, order_df):
    custNameKeyDf = col_as_keys(customerDf, COL_CUSTOMER_ID)

    #Combining Order and Customer DF
    for index, series in order_df.iterrows():
        if series[COL_CUSTOMER_ID] in custNameKeyDf.keys():
            order_df.at[index, COL_HP] = custNameKeyDf[series[COL_CUSTOMER_ID]][1]
            order_df.at[index, COL_ADDRESS] = custNameKeyDf[series[COL_CUSTOMER_ID]][3]
            order_df.at[index, COL_BIRTHDAY] = custNameKeyDf[series[COL_CUSTOMER_ID]][2]
            order_df.at[index, COL_EMAIL] = custNameKeyDf[series[COL_CUSTOMER_ID]][4]
        else:
            print(series["Name"] + " Not Found in Customer Data")
    
    #Drop customer_id col
    order_df.drop([COL_CUSTOMER_ID],axis=1,inplace=True)

    #Reordering columns
    cols = order_df.columns.tolist()
    cols = cols[0:4] + cols[-4:] + cols[4:-4]
    order_df = order_df[cols]

    return order_df #Combined Order and Customer DF
                

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
def generate_qty_table(df, default_qty_df, platform):
    unmatched_products = []
    for i, order_series in df.iterrows():
        order_str = order_series["Product"]
        order_dict = ast.literal_eval(order_str)
        pdt_components = {}
        for product_name, qty in order_dict.items():
            if (product_name in default_qty_df["title"].tolist()):
                for flavour in default_qty_df.columns.tolist()[2:]:
                    if flavour not in pdt_components.keys():
                        pdt_components[flavour] = qty * default_qty_df.at[default_qty_df[default_qty_df["title"]==product_name].index.values[0], flavour]
                    else:
                        pdt_components[flavour] += qty * default_qty_df.at[default_qty_df[default_qty_df["title"]==product_name].index.values[0], flavour]
            else:
                if len(unmatched_products) == 0:
                    unmatched_products.append(product_name)
                elif product_name not in unmatched_products:
                    unmatched_products.append(product_name)
                else:
                    pass
        for component, componentQty in pdt_components.items():
            df.at[i,component] = componentQty

    if len(unmatched_products) > 0:
        print(f"Unmatched Products for {platform}: " + str(unmatched_products))
        # messagebox.showinfo("Unmatched Products", "There are unmatched products. Please check Settings to verify all product inputs.")

    return df, pd.Series(unmatched_products, name = "Unmatched Products")

#Adds one second to date
def add_one_sec_ISO(str_date):
    return pd.to_datetime(str_date) + timedelta(seconds=1)

#Converts date to ISO8601 format
def convert_ISO(date):
    try:
        date = parser.parse(date)
    except:
        pass
    convertedDate = date.isoformat()
    return convertedDate

#Converts date from ISO to epoch format
def convert_epoch(date):
    date = parser.isoparse(date).timestamp()
    return int(date)
