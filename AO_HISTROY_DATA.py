import configparser
from smartapi import SmartConnect
import os
import pyotp
import time
import pprint
import urllib
import json
import USER_DEFINE_PATHS as PATH
from datetime import datetime, date ,timedelta
#import datetime as dt
import AO_AUTH as ANGELONE
import PARAM.ERROR as ERROR
import AO_TOKEN_LIST as TOKEN
import sys
import pandas as pd
#import yaml

parser = configparser.ConfigParser()
parser.read('CONFIG.ini')

ERROR_CALLER = 1

ANGEL_ONE_OBJ = {}
ANGEL_ONE_RESPONSE_IN_LIST =[]
SAPI_OBJ = {}
SAPI_RES_SESS = {}
ANGEL_ONE_RESPONSE_IN_LIST_LEN = 0





FILE_PATH_EXIST = os.path.exists(PATH.CURRENT_JSON_RES_BANKNIFTY_FILEPATH)
FILE_TOKEN_FILTER_DATA = {}


DATA_STATUS_FUT = False
DATA_STATUS_CE = False
DATA_STATUS_PE = False
FUT_CURRENT_PRICE = 0
FUT_CURRENT_SYMBOL =''
FUT_CURRENT_TOKEN_NUMBER =  ''
MONTHLY_EX_DATE_FORM1 = ''
MONTHLY_EX_DATE_FORM2 =  ''
MONTHLY_REM_DAY = 0
OPT_CE = {}
OPT_PE = {}
RESPONSE_DATE_TIME =  ''
WEEKLY_EX_DATE_FORM1 = ''
WEEKLY_EX_DATE_FORM2 = ''
WEEKLY_REM_DAY = 0

ANGEL_ONE_OBJ = ANGELONE.ANGEL_ONE()

def SMART_API_OBJ_AND_RES():
    global ANGEL_ONE_OBJ
    global ANGEL_ONE_RESPONSE_IN_LIST
    global SAPI_OBJ
    global SAPI_RES_SESS
    global ANGEL_ONE_RESPONSE_IN_LIST_LEN
    
    ANGEL_ONE_RESPONSE_IN_LIST = ANGEL_ONE_OBJ.RETURN_SESSION_OBJ_AND_RESPONSE()
    ANGEL_ONE_RESPONSE_IN_LIST_LEN = len(ANGEL_ONE_RESPONSE_IN_LIST)
    if ANGEL_ONE_RESPONSE_IN_LIST_LEN > 0:
        SAPI_OBJ = ANGEL_ONE_RESPONSE_IN_LIST[0]
        SAPI_RES_SESS = ANGEL_ONE_RESPONSE_IN_LIST[1]
        return SAPI_OBJ
    return {}


def PATH_VALIDATE(FILE_PATH_EXIST):
    if not bool(FILE_PATH_EXIST):
        return False
    else:
        return True

def JSON_PATH_VALIDATE():
    JSON_FILE_PATH_EXIST = os.path.exists(PATH.CURRENT_JSON_RES_BANKNIFTY_FILEPATH)
    if not bool(JSON_FILE_PATH_EXIST):
        return False
    else:
        return True    
    
def JSON_FILE_DATA_LOAD():
    FILE_JSON_LOAD_DATA = {}
    FILE_DATA = open(PATH.CURRENT_JSON_RES_BANKNIFTY_FILEPATH)
    if bool(FILE_DATA):
        FILE_JSON_LOAD_DATA = json.load(FILE_DATA)
    return FILE_JSON_LOAD_DATA

def FILE_TOKEN_FILTER_DATA_VALIDATOR(FILE_TOKEN_FILTER_DATA):
    global DATA_STATUS
    global DATA_STATUS_FUT
    global DATA_STATUS_CE
    global DATA_STATUS_PE
    global FUT_CURRENT_PRICE
    global FUT_CURRENT_SYMBOL
    global FUT_CURRENT_TOKEN_NUMBER
    global MONTHLY_EX_DATE_FORM1
    global MONTHLY_EX_DATE_FORM2
    global MONTHLY_REM_DAY
    global OPT_CE
    global OPT_PE
    global RESPONSE_DATE_TIME
    global WEEKLY_EX_DATE_FORM1
    global WEEKLY_EX_DATE_FORM2
    global WEEKLY_REM_DAY
    
    if bool(FILE_TOKEN_FILTER_DATA):
        pprint.pprint(FILE_TOKEN_FILTER_DATA)
        if "DATA_STATUS_FUT" in FILE_TOKEN_FILTER_DATA.keys():
            DATA_STATUS_FUT = FILE_TOKEN_FILTER_DATA['DATA_STATUS_FUT']
            
        if "DATA_STATUS_CE" in FILE_TOKEN_FILTER_DATA.keys():
            DATA_STATUS_CE = FILE_TOKEN_FILTER_DATA['DATA_STATUS_CE']
            
        if "DATA_STATUS_PE" in FILE_TOKEN_FILTER_DATA.keys():
            DATA_STATUS_PE = FILE_TOKEN_FILTER_DATA['DATA_STATUS_PE']
            
        if "FUT_CURRENT_PRICE" in FILE_TOKEN_FILTER_DATA.keys():
            FUT_CURRENT_PRICE = FILE_TOKEN_FILTER_DATA['FUT_CURRENT_PRICE']
            
        if "FUT_CURRENT_SYMBOL" in FILE_TOKEN_FILTER_DATA.keys():
            FUT_CURRENT_SYMBOL = FILE_TOKEN_FILTER_DATA['FUT_CURRENT_SYMBOL']
            
        if "FUT_CURRENT_TOKEN_NUMBER" in FILE_TOKEN_FILTER_DATA.keys():
            FUT_CURRENT_TOKEN_NUMBER = FILE_TOKEN_FILTER_DATA['FUT_CURRENT_TOKEN_NUMBER']
        
        if "MONTHLY_EX_DATE_FORM1" in FILE_TOKEN_FILTER_DATA.keys():
            MONTHLY_EX_DATE_FORM1 = FILE_TOKEN_FILTER_DATA['MONTHLY_EX_DATE_FORM1']

        if "MONTHLY_EX_DATE_FORM2" in FILE_TOKEN_FILTER_DATA.keys():
            MONTHLY_EX_DATE_FORM2 = FILE_TOKEN_FILTER_DATA['MONTHLY_EX_DATE_FORM2']
            
        if "MONTHLY_REM_DAY" in FILE_TOKEN_FILTER_DATA.keys():
            MONTHLY_REM_DAY = FILE_TOKEN_FILTER_DATA['MONTHLY_REM_DAY']
            
        if "OPT_CE" in FILE_TOKEN_FILTER_DATA.keys():
            OPT_CE = FILE_TOKEN_FILTER_DATA['OPT_CE']
            
        if "OPT_PE" in FILE_TOKEN_FILTER_DATA.keys():
            OPT_PE = FILE_TOKEN_FILTER_DATA['OPT_PE']
            
        if "RESPONSE_DATE_TIME" in FILE_TOKEN_FILTER_DATA.keys():
            RESPONSE_DATE_TIME = FILE_TOKEN_FILTER_DATA['RESPONSE_DATE_TIME']
            
        if "WEEKLY_EX_DATE_FORM1" in FILE_TOKEN_FILTER_DATA.keys():
            WEEKLY_EX_DATE_FORM1 = FILE_TOKEN_FILTER_DATA['WEEKLY_EX_DATE_FORM1']
            
        if "WEEKLY_EX_DATE_FORM2" in FILE_TOKEN_FILTER_DATA.keys():
            WEEKLY_EX_DATE_FORM2 = FILE_TOKEN_FILTER_DATA['WEEKLY_EX_DATE_FORM2']

        if "WEEKLY_REM_DAY" in FILE_TOKEN_FILTER_DATA.keys():
            WEEKLY_REM_DAY = FILE_TOKEN_FILTER_DATA['WEEKLY_REM_DAY']

def JSON_DATA_PROCESS():
    global DATA_STATUS
    global DATA_STATUS_FUT
    global DATA_STATUS_CE
    global DATA_STATUS_PE
    FILE_TOKEN_FILTER_DATA = JSON_FILE_DATA_LOAD()
    FILE_TOKEN_FILTER_DATA_VALIDATOR(FILE_TOKEN_FILTER_DATA)
    if DATA_STATUS_FUT and DATA_STATUS_CE and DATA_STATUS_PE:
        return True
    else:
        return False
                  
def ANGEL_TOKEN_FILTER_DATA_VALIDATOR():
    global FILE_PATH_EXIST
    global FILE_TOKEN_FILTER_DATA
    R = False
    print("JSON_PATH_VALIDATE",JSON_PATH_VALIDATE())
    
    if JSON_PATH_VALIDATE():
        R = JSON_DATA_PROCESS() 
    else:
        RES = TOKEN.ANGEL_TOKEN_LIST_FILE_SAVE(FORCE=True) 
        time.sleep(2)
        if JSON_PATH_VALIDATE():
          R = JSON_DATA_PROCESS()
        else:
           print(ERROR.E5) 
           return R
           
    if R == True:
       return R
    else: 
       print("ERORR: JSON DATA IS NOT SET") 
       return R



def HISTORICAL_DATA():

    ## IMP FUT_CURRENT_TOKEN_NUMBER
    global FUT_CURRENT_TOKEN_NUMBER
    
    global ANGEL_ONE_OBJ
    global ANGEL_ONE_RESPONSE_IN_LIST
    global SAPI_OBJ
    global SAPI_RES_SESS
    global ANGEL_ONE_RESPONSE_IN_LIST_LEN
    
    DURATION = 120
    TIME_INTERVAL = "ONE_HOUR"
    FROM_DATE = (date.today() - timedelta(DURATION)).strftime('%Y-%m-%d %H:%M')
    END_DATE = date.today().strftime('%Y-%m-%d %H:%M') 
    
    ANGEL_TOKEN_FILTER_DATA_VALIDATOR()
    SMART_API_OBJ_AND_RES()
    
    if FUT_CURRENT_TOKEN_NUMBER != '':
        
        # exchange:OPTIDX
        # exchange:NFO
        # exchange:NSE
        params = {
              "exchange": "NFO",
              "symboltoken": FUT_CURRENT_TOKEN_NUMBER,
              "interval": TIME_INTERVAL,
              "fromdate": FROM_DATE,
              "todate": END_DATE
            }
        try:
            HIST_DATA = SAPI_OBJ.getCandleData(params)
        except:
            print("ERROR:ISSUE WITH SAPI_OBJ.getCandleData function please check parameters")
            exit()
            
        HIST_DATA_ROW = []
    
        KEY = "data"
        if KEY in HIST_DATA.keys():
            HIST_DATA_ROW = HIST_DATA[KEY]
            if HIST_DATA_ROW != None:    
               HIST_DATA_DF = pd.DataFrame(HIST_DATA_ROW,columns = ["date","open","high","low","close","volume"])
               HIST_DATA_DF.set_index("date",inplace=True)
               print(HIST_DATA_DF)
            #    HIST_DATA_DF.set_index("date",inplace=True)
               HIST_DATA_DF.index = pd.to_datetime(HIST_DATA_DF.index)
               HIST_DATA_DF.index = HIST_DATA_DF.index.tz_localize(None)
               HIST_DATA_DF.drop_duplicates(keep="first",inplace=True)
               
               return HIST_DATA_DF
            else:
               print("DATA: DATA IS EMPTY OR NONE")
               exit()  
        else:
            print("DATA: DATA KEY NOT FOUND")
            exit()


HIST_DATA_DF = HISTORICAL_DATA()
print(HIST_DATA_DF)
# HIST_DATA_DF['V_Price'] = (HIST_DATA_DF['close']-HIST_DATA_DF['open'])*HIST_DATA_DF['volume']
# HIST_DATA_DF['VWAP'] = HIST_DATA_DF['V_Price'].rolling('2d').mean()/HIST_DATA_DF['volume'].rolling('2d').mean()
# HIST_DATA_DF['VW_G_o'] = HIST_DATA_DF['open'] > HIST_DATA_DF['VWAP']
# HIST_DATA_DF['VW_s_o'] = HIST_DATA_DF['open'] < HIST_DATA_DF['VWAP']
# HIST_DATA_DF['VW_G_c'] = HIST_DATA_DF['close'] > HIST_DATA_DF['VWAP']
# HIST_DATA_DF['VW_s_c'] = HIST_DATA_DF['close'] < HIST_DATA_DF['VWAP']
# HIST_DATA_DF['VW_G_l'] = HIST_DATA_DF['low'] > HIST_DATA_DF['VWAP']
# HIST_DATA_DF['VW_s_l'] = HIST_DATA_DF['low'] < HIST_DATA_DF['VWAP']
# HIST_DATA_DF['VW_G_h'] = HIST_DATA_DF['high'] > HIST_DATA_DF['VWAP']
# HIST_DATA_DF['VW_s_h'] = HIST_DATA_DF['high'] < HIST_DATA_DF['VWAP']

# HIST_DATA_DF = HIST_DATA_DF.assign(
#     vwap=HIST_DATA_DF.eval(
#         'wgtd = price * quantity', inplace=False
#     ).groupby(HIST_DATA_DF.index.date).cumsum().eval('wgtd / quantity')
# )
print(HIST_DATA_DF)
# def HISTORICAL_DATA(TOEKEN_ID,START_DATE,END_DATE,TIME_INTERVAL):
#     params = {
#              "exchange": "NSE",
#              "symboltoken": TOEKEN_ID,
#              "interval": TIME_INTERVAL,
#              "fromdate": START_DATE,
#              "todate": END_DATE
#              }
#     hist_data = obj.getCandleData(params)
#     df_data = pd.DataFrame(hist_data["data"],
#                            columns = ["date","open","high","low","close","volume"])
#     df_data.set_index("date",inplace=True)
#     return df_data
