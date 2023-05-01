# -*- coding: utf-8 -*-
"""
Angel One - Bollinger Band Technical Indicator

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
import os
import urllib
import json
import pandas as pd
import datetime as dt
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


def hist_data(tickers,duration,interval,instrument_list,exchange="NSE"):
    hist_data_tickers = {} 
    for ticker in tickers:
        params = {
                 "exchange": exchange,
                 "symboltoken": token_lookup(ticker,instrument_list),
                 "interval": interval,
                 "fromdate": (dt.date.today() - dt.timedelta(duration)).strftime('%Y-%m-%d %H:%M'),
                 "todate": dt.datetime.now().strftime('%Y-%m-%d %H:%M')  
                 }
        hist_data = obj.getCandleData(params)
        df_data = pd.DataFrame(hist_data["data"],
                               columns = ["date","open","high","low","close","volume"])
        df_data.set_index("date",inplace=True)
        df_data.index = pd.to_datetime(df_data.index)
        df_data.index = df_data.index.tz_localize(None)
        hist_data_tickers[ticker] = df_data
    return hist_data_tickers

candle_data = hist_data(["HDFC","HCLTECH"], 2, "FIVE_MINUTE", instrument_list)

def bollBand(df_dict, n=20):
    "function to calculate Bollinger Band"
    for df in df_dict:
        df_dict[df]["MB"] = df_dict[df]["close"].rolling(n).mean()
        df_dict[df]["UB"] = df_dict[df]["MB"] + 2*df_dict[df]["close"].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
        df_dict[df]["LB"] = df_dict[df]["MB"] - 2*df_dict[df]["close"].rolling(n).std(ddof=0) #ddof=0 is required since we want to take the standard deviation of the population and not sample
        df_dict[df]["BB_Width"] = df_dict[df]["UB"] -  df_dict[df]["LB"] 
        
bollBand(candle_data)



















