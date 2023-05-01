import configparser
import os
import urllib
import json
import pandas as pd
import nse_api as napi
import PARAM.ERROR as ERROR
import USER_DEFINE_PATHS as PATH
import pprint
from datetime import datetime, date
import sys

parser = configparser.ConfigParser()
parser.read("CONFIG.ini")

## INITATION
NSE_DATA_DICT = {}
current_expiry_date = ""
EXPIRYDATA = ""
Last_price = 0
STRIKE_PRICE_BASE = CE_STRIKE_PRICE = PE_STRIKE_PRICE = 0
CE_SP_UP = CE_SP_LOW = PE_SP_UP = PE_SP_LOW = 0

TODAY_DATE = date.today()
DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT2 = "%d%b%Y"

TODAY_DATE_FORM1 = TODAY_DATE.strftime(DATE_FORMAT)
TODAY_DATE_FORM2 = datetime.strptime(TODAY_DATE_FORM1, DATE_FORMAT)

def DIFF_IN_DAYS_TODAY_DATE_WITH_EXPIRYDATE(EXPIRY_DATE):
    global TODAY_DATE_FORM2
    EXPIRY_AND_CURRENT_DATE_DELTA_DIFF = (EXPIRY_DATE - TODAY_DATE_FORM2)
    return EXPIRY_AND_CURRENT_DATE_DELTA_DIFF.days
    
def NSE_API_CALL():
    global NSE_DATA_DICT
    if not bool(NSE_DATA_DICT):
        NSE_DATA_DICT = napi.get_filter_data()
    return NSE_DATA_DICT

def NSE_API_DATA():
    NSE_DATA_DICT = NSE_API_CALL()
    if bool(NSE_DATA_DICT):
        if "current_expiry_date" not in NSE_DATA_DICT:
            print(ERROR.E1)
            exit()

        if "Last_price" not in NSE_DATA_DICT:
            print(ERROR.E2)
            exit()
        return NSE_DATA_DICT
    else:
        print(ERROR.E3)
        exit()

def ANGEL_INSTRUMENT_LIST():
    INSTRUMENT_LIST_URL = parser.get("URL", "INSTRUMENT_LIST")
    response = urllib.request.urlopen(INSTRUMENT_LIST_URL)
    instrument_list = json.loads(response.read())
    return instrument_list

def FUTURE_FILE_SAVE(TOK_DF):
    global TODAY_DATE_FORM1
    global DATE_FORMAT2
    RETURN_FUT_OBJ = {}
    RETURN_FUT_OBJ["FUTURE_FILE_STATUS"] = False
    RETURN_FUT_OBJ["DAY_REM_FOR_MONTHLY_EXPIRY"] = ""
    RETURN_FUT_OBJ["MONTH_EXPIRY_FORMAT1"] = ""
    RETURN_FUT_OBJ["MONTH_EXPIRY_FORMAT2"] = ""
    RETURN_FUT_OBJ["CURRENT_FUTURE_TOKEN_NUMBER"] = ""
    RETURN_FUT_OBJ["CURRENT_FUTURE_TOKEN_symbol"] = ""

    ANGEL_BN_FUT_TOK_DF = pd.DataFrame(TOK_DF[(TOK_DF["name"] == "BANKNIFTY") & (TOK_DF["instrumenttype"] == "FUTIDX") & (TOK_DF["lotsize"] == "25")])

    ANGEL_BN_FUT_TOK_DF["expiry1"] = pd.to_datetime(ANGEL_BN_FUT_TOK_DF["expiry"], format=DATE_FORMAT2)
    ANGEL_BN_FUT_TOK_DF = ANGEL_BN_FUT_TOK_DF.sort_values(by="expiry1")
    RETURN_FUT_OBJ["TODAY_DATE"] = TODAY_DATE_FORM1

    if not ANGEL_BN_FUT_TOK_DF.empty:
        ANGEL_BN_FUT_FILTER_DF = pd.DataFrame(ANGEL_BN_FUT_TOK_DF[(ANGEL_BN_FUT_TOK_DF["expiry1"] >= TODAY_DATE_FORM1)])
        if not ANGEL_BN_FUT_FILTER_DF.empty:
            try:
                ANGEL_BN_FUT_FILTER_DF.to_csv(PATH.FUT_ANGEL_BANKNIFTY_TOKENID_FILEPATH)
                CURRENT_FUT_DATA = ANGEL_BN_FUT_FILTER_DF.iloc[0]
                if not CURRENT_FUT_DATA.empty:
                    CURRENT_FUT_EXPIRY_DATE = CURRENT_FUT_DATA["expiry1"]
                    EXPIRY_AND_CURRENT_DATE_DELTA_DIFF_DAYS = DIFF_IN_DAYS_TODAY_DATE_WITH_EXPIRYDATE(CURRENT_FUT_EXPIRY_DATE)
                    RETURN_FUT_OBJ["FUTURE_FILE_STATUS"] = True
                    RETURN_FUT_OBJ["DAY_REM_FOR_MONTHLY_EXPIRY"] = EXPIRY_AND_CURRENT_DATE_DELTA_DIFF_DAYS
                    RETURN_FUT_OBJ["MONTH_EXPIRY_FORMAT1"] = CURRENT_FUT_DATA["expiry"]
                    RETURN_FUT_OBJ["MONTH_EXPIRY_FORMAT2"] = str(CURRENT_FUT_EXPIRY_DATE)
                    RETURN_FUT_OBJ["CURRENT_FUTURE_TOKEN_NUMBER"] = CURRENT_FUT_DATA["token"]
                    RETURN_FUT_OBJ["CURRENT_FUTURE_TOKEN_symbol"] = CURRENT_FUT_DATA["symbol"]
                    return RETURN_FUT_OBJ
            except OSError:
                return RETURN_FUT_OBJ
        else:
            return RETURN_FUT_OBJ
    else:
        return RETURN_FUT_OBJ

def OPT_FILE_SAVE(ANGEL_BN_OPT_TOK_DF, NSE_DATA_DICT):

    EXPIRYDATA = NSE_DATA_DICT["EXPIRYDATA"]
    Last_price = NSE_DATA_DICT["Last_price"]
    CE_SP_UP = NSE_DATA_DICT["CE_SP_UP_R_VALUE"]
    CE_SP_LOW = NSE_DATA_DICT["CE_SP_LOW_R_VALUE"]
    PE_SP_UP = NSE_DATA_DICT["PE_SP_UP_R_VALUE"]
    PE_SP_LOW = NSE_DATA_DICT["PE_SP_LOW_R_VALUE"]


    df = pd.DataFrame(ANGEL_BN_OPT_TOK_DF)
    Last_price = int(Last_price)
    df["strike"] = pd.to_numeric(df["strike"])
    df["strike"] = df["strike"] / 100
    df["strike"] = df["strike"].astype("int64")
    df["symbol"] = df["symbol"].astype(str)
    df["ce_or_pe"] = df["symbol"].str[-2:].astype(str)
    CE_DF = df[(df["ce_or_pe"] == "CE")]
    PE_DF = df[(df["ce_or_pe"] == "PE")]
    CE_RANGE_DF = df[(df["ce_or_pe"] == "CE")]
    CE_DF = CE_DF[["token", "expiry", "strike"]]
    PE_DF = PE_DF[["token", "expiry", "strike"]]
 
    CE_RANGE_DF = CE_DF[(CE_DF["strike"] <= CE_SP_UP) & (CE_DF["strike"] >= CE_SP_LOW)]
    PE_RANGE_DF = PE_DF[(PE_DF["strike"] <= PE_SP_UP) & (PE_DF["strike"] >= PE_SP_LOW)]

    CE_RANGE_DF = CE_RANGE_DF.sort_values(by=["strike"], ignore_index=True)
    PE_RANGE_DF = PE_RANGE_DF.sort_values(by=["strike"], ignore_index=True)
    
    CE_RANGE_RAW_DICT_DF = pd.DataFrame(CE_RANGE_DF[["token","strike"]])
    PE_RANGE_RAW_DICT_DF = pd.DataFrame(PE_RANGE_DF[["token","strike"]])
    
    CE_RANGE_RAW_DICT_index_DF = CE_RANGE_RAW_DICT_DF.set_index('strike')
    PE_RANGE_RAW_DICT_index_DF = PE_RANGE_RAW_DICT_DF.set_index('strike')

    CE_RANGE_DF_DICT = CE_RANGE_RAW_DICT_index_DF.to_dict()
    PE_RANGE_DF_DICT = PE_RANGE_RAW_DICT_index_DF.to_dict()

    CE_RANGE_TOKEN_DICT = {}
    PE_RANGE_TOKEN_DICT = {}
    
    if bool(CE_RANGE_DF_DICT):
        if "token" in CE_RANGE_DF_DICT.keys():
            CE_RANGE_TOKEN_DICT = CE_RANGE_DF_DICT['token']
            
    if bool(PE_RANGE_DF_DICT):    
        if "token" in PE_RANGE_DF_DICT.keys():
            PE_RANGE_TOKEN_DICT = PE_RANGE_DF_DICT['token']

    RETURN_OBJ = {}
    RETURN_OBJ["CE_TOKEN_DATA_STATUS"] = True if not CE_RANGE_DF.empty else False
    RETURN_OBJ["PE_TOKEN_DATA_STATUS"] = True if not PE_RANGE_DF.empty else False
    RETURN_OBJ["CE_TOKEN_RANGE_DICT"] = CE_RANGE_TOKEN_DICT
    RETURN_OBJ["PE_TOKEN_RANGE_DICT"] = PE_RANGE_TOKEN_DICT
    RETURN_OBJ["EXPIRYDATA"] = EXPIRYDATA
    RETURN_OBJ["Last_price"] = Last_price

    return RETURN_OBJ

def ANGEL_TOKEN_JSON_DATA(FORCE=False):
    FILE_PATH_EXIST = os.path.exists(PATH.CURRENT_JSON_RES_BANKNIFTY_FILEPATH)
    if bool(FILE_PATH_EXIST) and FORCE == False:
        f = open(PATH.CURRENT_JSON_RES_BANKNIFTY_FILEPATH)
        data = json.load(f)
        return data
        
    global DATE_FORMAT2
    RETURN_DICT = {}
    RETURN_DICT['DATA_STATUS_FUT'] = False
    RETURN_DICT['DATA_STATUS_CE'] = False
    RETURN_DICT['DATA_STATUS_PE'] = False
    
    CE_OPT_FILE_STATUS = False
    PE_OPT_FILE_STATUS = False

    
    
    INSTRUMENT_DATA = ANGEL_INSTRUMENT_LIST()
    TOK_DF = pd.DataFrame(INSTRUMENT_DATA)
    FUT_FILE_STATUS = FUTURE_FILE_SAVE(TOK_DF)
    print(FUT_FILE_STATUS)

    NSE_DATA_DICT = NSE_API_DATA()
    EXPIRYDATA = NSE_DATA_DICT["EXPIRYDATA"]
    Last_price = NSE_DATA_DICT["Last_price"]
    
    if Last_price != 0 and EXPIRYDATA != "":
        ANGEL_BN_OPT_TOK_DF = TOK_DF[
            (TOK_DF["name"] == "BANKNIFTY")
            & (TOK_DF["instrumenttype"] == "OPTIDX")
            & (TOK_DF["lotsize"] == "25")
            & (TOK_DF["expiry"] == EXPIRYDATA)
        ]
        OPT_FILE_STATUS = OPT_FILE_SAVE(ANGEL_BN_OPT_TOK_DF, NSE_DATA_DICT)

        
        if bool(FUT_FILE_STATUS):
            if "FUTURE_FILE_STATUS" in FUT_FILE_STATUS.keys():
                FUTURE_FILE_STATUS = FUT_FILE_STATUS["FUTURE_FILE_STATUS"]
                print("FUTURE_FILE_STATUS",FUTURE_FILE_STATUS),
                DAY_REM_FOR_MONTHLY_EXPIRY = FUT_FILE_STATUS["DAY_REM_FOR_MONTHLY_EXPIRY"]
                CURRENT_FUTURE_TOKEN_NUMBER = FUT_FILE_STATUS["CURRENT_FUTURE_TOKEN_NUMBER"]
                CURRENT_FUTURE_TOKEN_symbol = FUT_FILE_STATUS["CURRENT_FUTURE_TOKEN_symbol"]
                
                RETURN_DICT['DATA_STATUS_FUT'] = FUTURE_FILE_STATUS if FUTURE_FILE_STATUS == True else False
                RETURN_DICT['MONTHLY_EX_DATE_FORM1'] = FUT_FILE_STATUS["MONTH_EXPIRY_FORMAT1"]
                RETURN_DICT['MONTHLY_EX_DATE_FORM2'] = FUT_FILE_STATUS["MONTH_EXPIRY_FORMAT2"]
                RETURN_DICT['MONTHLY_REM_DAY'] = DAY_REM_FOR_MONTHLY_EXPIRY
                RETURN_DICT['FUT_CURRENT_SYMBOL'] = CURRENT_FUTURE_TOKEN_symbol
                RETURN_DICT['FUT_CURRENT_TOKEN_NUMBER'] = CURRENT_FUTURE_TOKEN_NUMBER
                RETURN_DICT['FUT_CURRENT_PRICE'] = Last_price
               


        if "CE_TOKEN_DATA_STATUS" in OPT_FILE_STATUS.keys():
            CE_TOKEN_DATA_STATUS = OPT_FILE_STATUS["CE_TOKEN_DATA_STATUS"]
            CE_RANGE_TOKEN_DICT = OPT_FILE_STATUS["CE_TOKEN_RANGE_DICT"]
            RETURN_DICT['OPT_CE'] = CE_RANGE_TOKEN_DICT
            RETURN_DICT['DATA_STATUS_CE'] = CE_TOKEN_DATA_STATUS if CE_TOKEN_DATA_STATUS == True else False
            

        if "PE_TOKEN_DATA_STATUS" in OPT_FILE_STATUS.keys():
            PE_TOKEN_DATA_STATUS = OPT_FILE_STATUS["PE_TOKEN_DATA_STATUS"]
            PE_TOKEN_RANGE_DICT = OPT_FILE_STATUS["PE_TOKEN_RANGE_DICT"]
            RETURN_DICT['OPT_PE'] = PE_TOKEN_RANGE_DICT
            RETURN_DICT['DATA_STATUS_PE'] = PE_TOKEN_DATA_STATUS if PE_TOKEN_DATA_STATUS == True else False
            

        if CE_TOKEN_DATA_STATUS == True and PE_TOKEN_DATA_STATUS  == True: 
            WEEKLY_EX_DATE_FORM2 = pd.to_datetime(OPT_FILE_STATUS["EXPIRYDATA"], format=DATE_FORMAT2)
            WEEKLY_REM_DAY = DIFF_IN_DAYS_TODAY_DATE_WITH_EXPIRYDATE(WEEKLY_EX_DATE_FORM2)         
            RETURN_DICT['WEEKLY_EX_DATE_FORM1'] = OPT_FILE_STATUS["EXPIRYDATA"]
            RETURN_DICT['WEEKLY_EX_DATE_FORM2'] = str(WEEKLY_EX_DATE_FORM2)
            RETURN_DICT['WEEKLY_REM_DAY'] = WEEKLY_REM_DAY
            
    RETURN_DICT["RESPONSE_DATE_TIME"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")    
    return RETURN_DICT


def ANGEL_TOKEN_LIST_FILE_SAVE(FORCE=False):
    JSON_DATA = ANGEL_TOKEN_JSON_DATA(FORCE)
    with open(PATH.CURRENT_JSON_RES_BANKNIFTY_FILEPATH, "w") as outfile:
        json.dump(JSON_DATA, outfile)
    return JSON_DATA
    
    
if __name__ == "__main__":
    
    COMMAND = ""
    SYS_ARGV = sys.argv
    SYS_ARGV_COUNT = len(SYS_ARGV)
    ANGEL_TOKEN_CUSTOM_JSON = {}
    COMMAND = SYS_ARGV[1] if SYS_ARGV_COUNT > 1 else COMMAND
    if COMMAND == 'F' or COMMAND == 'f':
        ANGEL_TOKEN_CUSTOM_JSON = ANGEL_TOKEN_LIST_FILE_SAVE(FORCE=True)
        pprint.pprint(ANGEL_TOKEN_CUSTOM_JSON)
    else:
        ANGEL_TOKEN_CUSTOM_JSON = ANGEL_TOKEN_LIST_FILE_SAVE()
        pprint.pprint(ANGEL_TOKEN_CUSTOM_JSON)