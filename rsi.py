# -*- coding: utf-8 -*-
"""
Angel One - RSI Technical Indicator using TradingView RMA implementation

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
import os
import urllib
import json
import numpy as np
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

candle_data = hist_data(["HDFC","HCLTECH"], 5, "FIVE_MINUTE", instrument_list)

def RMA(ser, n=9):
    multiplier = 1/n    
    sma = ser.rolling(n).mean()
    ema = np.full(len(ser), np.nan)
    ema[len(sma) - len(sma.dropna())] = sma.dropna()[0]
    for i in range(len(ser)):
        if not np.isnan(ema[i-1]):
            ema[i] = ((ser.iloc[i] - ema[i-1])*multiplier) + ema[i-1]
    ema[len(sma) - len(sma.dropna())] = np.nan
    return ema

def RSI(df_dict, n=14):
    "function to calculate RSI"
    for df in df_dict:
        df_dict[df]["change"] = df_dict[df]["close"] - df_dict[df]["close"].shift(1)
        df_dict[df]["gain"] = np.where(df_dict[df]["change"]>=0, df_dict[df]["change"], 0)
        df_dict[df]["loss"] = np.where(df_dict[df]["change"]<0, -1*df_dict[df]["change"], 0)
        df_dict[df]["avgGain"] = RMA(df_dict[df]["gain"],n)
        df_dict[df]["avgLoss"] = RMA(df_dict[df]["loss"],n)
        df_dict[df]["rs"] = df_dict[df]["avgGain"]/df_dict[df]["avgLoss"]
        df_dict[df]["rsi"] = 100 - (100/ (1 + df_dict[df]["rs"]))
        df_dict[df].drop(["change","gain","loss","avgGain","avgLoss","rs"], axis=1, inplace=True)
        
RSI(candle_data)












