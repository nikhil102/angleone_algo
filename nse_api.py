# Libraries
import requests
import json
import math
import pandas as pd
import pprint
import sqlite3 as sl
from sqhelper import SQHelper
from datetime import date
import configparser
import ast

parser = configparser.ConfigParser()
parser.read('CONFIG.ini')

STRIKE_PRICE_BASE = 0
STRIKE_PRICE_BASE = 0
CE_STRIKE_PRICE = 0
PE_STRIKE_PRICE = 0
CE_STRIKE_PRICE_UPPER_RANGE_VALUE = 0
CE_STRIKE_PRICE_LOWER_RANGE_VALUE = 0
PE_STRIKE_PRICE_UPPER_RANGE_VALUE = 0
PE_STRIKE_PRICE_LOWER_RANGE_VALUE = 0

url_bnf = parser.get('URL', 'NSE_BANKNIFTY_URL')
url_oc = parser.get('URL', 'NSE_BANKNIFTY_OPTION_CHAIN')


# Headers
header_string = parser.get('HEADERS', 'NSEAPI')
headers = ast.literal_eval(header_string)

sess = requests.Session()
cookies = dict()

# #con = sl.connect('my-test.db')
# db = 'myDatabase.sql3'
# database = SQHelper(db)


def set_cookie():
    request = sess.get(url_oc, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    
def get_data():
    set_cookie()
    response = sess.get(url_bnf, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==401):
        set_cookie()
        response = sess.get(url_bnf, headers=headers, timeout=5, cookies=cookies)
    if(response.status_code==200):
        return response.text
    return ""

def get_filter_data():
    res = get_data()
    if res == None or res == "":
       return {}
    else: 

        json_object = json.loads(res)        
        if bool(json_object):
            
           records = {}
           filtered = {}
           expiryDates= {}
           index= {}
           Last_price= 0
           expiryDates = []
           
           if 'records' in json_object:
               records = json_object['records']
           else:
               return {}
           
           if 'filtered' in json_object:
               filtered = json_object['filtered']
           else:
               return {}
           
           if 'expiryDates' in records:
               expiryDates = records['expiryDates']
           else:
               return {} 
           
           if 'index' in records:
               index = records['index']
           else:
               return {}
           
           if 'last' in index:
               Last_price = index['last']
           else:
               return {}
           
        if len(expiryDates) > 0:
            EX_ROW_DF = pd.DataFrame(expiryDates,columns = ['expiryDates'])
            EX_ROW_DF['expiryDates'] = pd.to_datetime(EX_ROW_DF['expiryDates'])
            today = date.today()
            TODAYDATE_CHECK= today.strftime('%Y-%b-%d')
            EX_DF = pd.DataFrame(EX_ROW_DF[(EX_ROW_DF['expiryDates']> TODAYDATE_CHECK)])
            EX_DF['expiryDates'] = EX_DF['expiryDates'].dt.strftime('%d%b%Y')
            EX_DF.reset_index(drop=True ,inplace = True)
            if not EX_DF.empty:
                current_expiry_date = EX_DF.expiryDates.iloc[0]  
        else:
            return {} 
            

        if current_expiry_date != "":
            EXPIRYDATA = str(current_expiry_date).upper()
        if int(Last_price) > 0:
            Last_price 
            Last_price = int(Last_price)
            STRIKE_PRICE_BASE = Last_price / 100
            STRIKE_PRICE_BASE = int(STRIKE_PRICE_BASE)
            CE_STRIKE_PRICE = STRIKE_PRICE_BASE * 100
            PE_STRIKE_PRICE = CE_STRIKE_PRICE + 100 
            CE_STRIKE_PRICE_UPPER_RANGE_VALUE = CE_STRIKE_PRICE + 1000
            CE_STRIKE_PRICE_LOWER_RANGE_VALUE = CE_STRIKE_PRICE - 1000
            PE_STRIKE_PRICE_UPPER_RANGE_VALUE = PE_STRIKE_PRICE + 1000
            PE_STRIKE_PRICE_LOWER_RANGE_VALUE = PE_STRIKE_PRICE - 1000
            
            new_entry = {
                     'current_expiry_date': current_expiry_date,
                     'EXPIRYDATA':EXPIRYDATA,
                     'Last_price': Last_price,
                     'CURRENT_PRICE': Last_price,
                     'CE_STRIKE_PRICE':CE_STRIKE_PRICE,
                     'PE_STRIKE_PRICE':PE_STRIKE_PRICE,
                     'CE_SP_UP_R_VALUE':CE_STRIKE_PRICE_UPPER_RANGE_VALUE,
                     'CE_SP_LOW_R_VALUE':CE_STRIKE_PRICE_LOWER_RANGE_VALUE,
                     'PE_SP_UP_R_VALUE':PE_STRIKE_PRICE_UPPER_RANGE_VALUE,
                     'PE_SP_LOW_R_VALUE':PE_STRIKE_PRICE_LOWER_RANGE_VALUE,
                     
                    }
        
        return new_entry

# database.insert("option_day_data", new_entry)
