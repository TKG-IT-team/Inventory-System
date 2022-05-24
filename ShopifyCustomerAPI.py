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
            url = f"https://{self.apiKey}:{self.password}@{self.hostname}/admin/api/{self.version}/customers.json?limit=250&fulfillment_status=any&since_id={last}&status=any"
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
            #?limit=250&fulfillment_status=unfulfilled&since_id={last}
            response = requests.request("GET", url)
            
            df=pd.DataFrame(response.json()['customers'])
            customers=pd.concat([customers,df])
            last=df['id'].iloc[-1]
            if len(df)<250:
                break
        return(customers)

    #Clean Data
    def clean(self, rawData): 
        cleanedData = rawData[['id','addresses', 'note', 'email','default_address']]

        addresses = []
        hps = []
        birthdays = []
        names = []
        # rowsToDelete = []
        
        for index, series in cleanedData.iterrows():
            if not series.empty:
                # cleanedData["Name"] = cleanedData['first_name'] + " " + cleanedData['last_name']
                if (not pd.isna(series["default_address"])):
                    names.append(series["default_address"]["name"].lower())
                else:
                    names.append("-")
                
                if len(series["addresses"])>0 and "address1" in series["addresses"][0].keys():
                    address = series['addresses'][0]["address1"]
                    addresses.append(address)
                else:
                    addresses.append("-")

                if len(series["addresses"])>0 and "phone" in series["addresses"][0].keys():
                    hp = series['addresses'][0]["phone"]
                    hps.append(hp)
                else:
                    hps.append("-")   

                if (series["note"]!=None):
                    birthdays.append(series['note'][10:-1])
                else:
                    birthdays.append("-")
                
                #Remove rows with no values 
                # if (names[-1]=="" or names[-1]=="-") and (addresses[-1]=="" or addresses[-1]=="-") and (hps[-1]=="" or hps[-1]=="-") and (birthdays[-1]=="" or birthdays[-1]=="-"):
                #     del names[-1]
                #     del addresses[-1]
                #     del hps[-1]
                #     del birthdays[-1]
                #     rowsToDelete.append(index)
        
        # cleanedData = cleanedData.drop(cleanedData.index[rowsToDelete])

        cleanedData["Address"] = addresses
        cleanedData["HP"] = hps
        cleanedData["Birthday"] = birthdays
        cleanedData["Name"] = names
        del cleanedData['addresses']
        del cleanedData['note']
        del cleanedData['default_address']
        cleanedData = cleanedData.rename(columns={"email":"Email"})
        cleanedData = cleanedData[["Name", "HP", "Birthday", "Address", "Email"]]

        print(cleanedData)
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
