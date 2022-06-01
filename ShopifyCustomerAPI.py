from cmath import nan
import numpy as np
import re
import requests
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook

currTime = str(datetime.now())
formattedCurrTime = currTime[:9] + "T" + currTime[11:18]

class ShopifyCustomerAPI:
    def __init__(self, apiKey, password, hostname, version):
        self.apiKey = apiKey
        self.password = password
        self.hostname = hostname
        self.version = version

    #Get new customers in Shopify based on given last Customer ID
    def getNewCusts(self, lastCustId): #Get new customers after the existing newest customer ID in database
        last = lastCustId
        customers=pd.DataFrame()

        while True:
            url = f"https://{self.apiKey}:{self.password}@{self.hostname}/admin/api/{self.version}/customers.json?limit=250&fulfillment_status=any&status=any&since_id={last}"
            #?limit=250&fulfillment_status=any&status=any&since_id={last}
            response = requests.request("GET", url)
            df=pd.DataFrame(response.json()['customers'])
            customers=pd.concat([customers,df])
            last=df['id'].iloc[-1]
            if len(df)<250:
                break
        return(customers)

    #Get all customers in Shopify 
    def getAllCusts(self):
        last=0
        customers=pd.DataFrame()

        while True:
            url = f"https://{self.apiKey}:{self.password}@{self.hostname}/admin/api/{self.version}/customers.json?limit=250&fulfillment_status=any&since_id={last}&status=any"
            response = requests.request("GET", url)
            
            df=pd.DataFrame(response.json()['customers'])
            customers=pd.concat([customers,df])
            last=df['id'].iloc[-1]
            if len(df)<250:
                break
        return(customers)

    #Clean Data
    def clean(self, rawData): 
        cleanedData = rawData[['id','addresses', 'note', 'email','default_address','phone', 'email_marketing_consent', 'sms_marketing_consent']]
        cleanedData = cleanedData.reset_index(drop=True)

        # rowsToDelete = []
        
        for index, series in cleanedData.iterrows():
            if not series.empty:
                
                if (not pd.isna(series["default_address"])):
                    #Get Name and ID
                    cleanedData.at[index, "Name"] = series["default_address"]["name"].lower()
                    cleanedData.at[index, "Customer_id"] = series["default_address"]["customer_id"]
                else:
                    cleanedData.at[index, "Name"] = "-"

                #Get  Address
                if len(series["addresses"])>0 and "address1" in series["addresses"][0].keys():
                    address = series['addresses'][0]["address1"]
                    cleanedData.at[index, "Address"] = address
                else:
                    cleanedData.at[index, "Address"] = "-"

                # if len(series["addresses"])>0 and "phone" in series["addresses"][0].keys():
                #     hp = series['addresses'][0]["phone"]
                #     cleanedData.at[index, "HP"] = hp
                # else:
                #     cleanedData.at[index, "HP"] = "-"
                
                #Get Note
                if (series["note"]!=None):
                    cleanedData.at[index, "Birthday"] = series['note'][10:-1]
                else:
                    cleanedData.at[index, "Birthday"] = "-"

                #Get Email Marketing
                if (series["email_marketing_consent"]!=None):
                    cleanedData.at[index, "Email Consent"] = series["email_marketing_consent"]["state"]
                else:
                    cleanedData.at[index, "Email Consent"] = "-"

                #Get SMS Marketing
                if (series["sms_marketing_consent"]!=None):
                    cleanedData.at[index, "SMS Consent"] = series["sms_marketing_consent"]["state"]
                else:
                    cleanedData.at[index, "SMS Consent"] = "-"
                                    
                #Remove rows with no values 
                # if (names[-1]=="" or names[-1]=="-") and (addresses[-1]=="" or addresses[-1]=="-") and (hps[-1]=="" or hps[-1]=="-") and (birthdays[-1]=="" or birthdays[-1]=="-"):
                #     del names[-1]
                #     del addresses[-1]
                #     del hps[-1]
                #     del birthdays[-1]
                #     rowsToDelete.append(index)
        
        # cleanedData = cleanedData.drop(cleanedData.index[rowsToDelete])
        del cleanedData['addresses']
        del cleanedData['note']
        del cleanedData['default_address']
        cleanedData = cleanedData.rename(columns={"email":"Email", "phone":"HP"})
        cleanedData = cleanedData[["Customer_id", "Name", "HP", "Birthday", "Address", "Email","Email Consent","SMS Consent"]]

        return cleanedData

    #Adding on to existing Customer List
    #note: will be faster but old customers' details will not be updated
    def updateCustDf(self, oldCustDf):  #oldCustList in pandas dataframe
        lastCustId = oldCustDf["id"].iloc[-1]
        customers = self.getNewCusts(lastCustId)
        newCustDf = self.clean(customers)
        combinedDf = lastCustId.append(newCustDf, ignore_index=True)
        return combinedDf
    
    #Generate new xlsx backend file to read, replaces old version if there is
    #note: will be slower but old customers' details will be updated
    def generateFullCustDf(self): 
        customers = self.getAllCusts()
        cleanedData = self.clean(customers)
        return cleanedData
