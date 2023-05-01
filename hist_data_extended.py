# -*- coding: utf-8 -*-
"""
Angel One - Candle data over extended period

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
import os
import urllib
import json
import pandas as pd
import datetime as dt
import time
from pyotp import TOTP

key_path = r"D:\OneDrive\Udemy\Angel One API"
os.chdir(key_path)

key_secret = open("key.txt","r").read().split()

obj=SmartConnect(api_key=key_secret[0])
data = obj.generateSession(key_secret[2],key_secret[3],TOTP(key_secret[4]).now())

instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = urllib.request.urlopen(instrument_url)
instrument_list = json.loads(response.read())

def token_lookup(ticker, instrument_list, exchange="NSE"):
    for instrument in instrument_list:
        if instrument["name"] == ticker and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[-1] == "EQ":
            return instrument["token"]
        
def symbol_lookup(token, instrument_list, exchange="NSE"):
    for instrument in instrument_list:
        if instrument["token"] == token and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[-1] == "EQ":
            return instrument["name"]


def hist_data_extended(ticker,duration,interval,instrument_list,exchange="NSE"):
    st_date = dt.date.today() - dt.timedelta(duration)
    end_date = dt.date.today()
    st_date = dt.datetime(st_date.year, st_date.month, st_date.day, 9, 15)
    end_date = dt.datetime(end_date.year, end_date.month, end_date.day)
    df_data = pd.DataFrame(columns=["date","open","high","low","close","volume"])
    
    while st_date < end_date:
        time.sleep(0.4) #avoiding throttling rate limit
        params = {
                 "exchange": exchange,
                 "symboltoken": token_lookup(ticker,instrument_list),
                 "interval": interval,
                 "fromdate": (st_date).strftime('%Y-%m-%d %H:%M'),
                 "todate": (end_date).strftime('%Y-%m-%d %H:%M') 
                 }
        hist_data = obj.getCandleData(params)
        temp = pd.DataFrame(hist_data["data"],
                            columns = ["date","open","high","low","close","volume"])
        df_data = temp.append(df_data,ignore_index=True)
        #df_data = pd.concat([temp,df_data]) #above line may throw an error in later pandas versions. Use this line instead if that happens
        end_date = dt.datetime.strptime(temp['date'].iloc[0][:16], "%Y-%m-%dT%H:%M")
        if len(temp) <= 1: #this takes care of the edge case where start date and end date become same
            break

    df_data.set_index("date",inplace=True)
    df_data.index = pd.to_datetime(df_data.index)
    df_data.index = df_data.index.tz_localize(None)
    df_data.drop_duplicates(keep="first",inplace=True)    
    return df_data

hdfc_data = hist_data_extended("HDFC", 280, "ONE_HOUR", instrument_list)



















