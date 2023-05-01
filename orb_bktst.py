# -*- coding: utf-8 -*-
"""
Angel One - Opening Range Breakout strategy backtestin

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
import os
import urllib
import json
import pandas as pd
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

tickers = ["WIPRO","ULTRACEMCO","UPL","TITAN","TECHM","TATASTEEL","TATAMOTORS",
           "TATACONSUM","TCS","SUNPHARMA","SBIN","SBILIFE","RELIANCE","POWERGRID",
           "ONGC","NESTLEIND","NTPC","MARUTI","M&M","LT","KOTAKBANK","JSWSTEEL",
           "INFY","INDUSINDBK","ITC","ICICIBANK","HDFC","HINDUNILVR","HINDALCO",
           "HEROMOTOCO","HDFCLIFE","HDFCBANK","HCLTECH","GRASIM","EICHERMOT",
           "DRREDDY","DIVISLAB","COALINDIA","CIPLA","BRITANNIA","BHARTIARTL",
           "BPCL","BAJAJFINSV","BAJFINANCE","BAJAJ-AUTO","AXISBANK","ASIANPAINT",
           "APOLLOHOSP","ADANIPORTS","ADANIENT"]
bktst_start_dt = "2021-06-01 09:15"
bktst_end_dt = "2022-10-21 15:30"

def token_lookup(ticker, instrument_list, exchange="NSE"):
    for instrument in instrument_list:
        if instrument["name"] == ticker and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[-1] == "EQ":
            return instrument["token"]
        
def symbol_lookup(token, instrument_list, exchange="NSE"):
    for instrument in instrument_list:
        if instrument["token"] == token and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[-1] == "EQ":
            return instrument["name"]

def hist_data_daily(tickers,instrument_list,exchange="NSE"):
    hist_data_tickers = {} 
    for ticker in tickers:
        time.sleep(0.3)
        params = {
                 "exchange": exchange,
                 "symboltoken": token_lookup(ticker,instrument_list),
                 "interval": "ONE_DAY",
                 "fromdate": bktst_start_dt,
                 "todate": bktst_end_dt 
                 }
        hist_data = obj.getCandleData(params)
        df_data = pd.DataFrame(hist_data["data"],
                               columns = ["date","open","high","low","close","volume"])
        df_data.set_index("date",inplace=True)
        df_data.index = pd.to_datetime(df_data.index)
        df_data.index = df_data.index.tz_localize(None)
        df_data["gap"] = ((df_data["open"]/df_data["close"].shift(1))-1)*100
        df_data["avvol"] = df_data["volume"].rolling(10).mean().shift(1)
        hist_data_tickers[ticker] = df_data
    return hist_data_tickers

def hist_data_intraday(ticker,datestamp,interval,instrument_list,exchange="NSE"):
    params = {
             "exchange": exchange,
             "symboltoken": token_lookup(ticker,instrument_list),
             "interval": interval,
             "fromdate": datestamp.strftime("%Y-%m-%d")+ " 09:15",
             "todate": datestamp.strftime("%Y-%m-%d") + " 15:30" 
             }
    hist_data = obj.getCandleData(params)
    df_data = pd.DataFrame(hist_data["data"],
                           columns = ["date","open","high","low","close","volume"])
    df_data.set_index("date",inplace=True)
    df_data.index = pd.to_datetime(df_data.index)
    df_data.index = df_data.index.tz_localize(None)
    return df_data

candle_data = hist_data_daily(tickers, instrument_list)


def topGap(data):
    top_gap_by_date = {}
    dates = data[tickers[0]].index.to_list()    
    for date in dates:
        temp = pd.Series()
        for ticker in data:
            try:
                temp.loc[ticker] = data[ticker].loc[date,"gap"]
            except:
                pass
        top_gap_by_date[date] = (abs(temp[abs(temp)>1.5])).sort_values(ascending=False)[:5].index.to_list()
        print("top 5 gap stocks on {}".format(date))
        print((abs(temp[abs(temp)>1.5])).sort_values(ascending=False)[:5])
    
    return top_gap_by_date

top_gap_by_date = topGap(candle_data)


def backtest(top_gap_by_date, candle_data):
    date_stats = {}
    for date in top_gap_by_date:
        date_orgnl = date.strftime("%Y-%m-%d %H:%M")
        date_stats[date] = {}
        for ticker in top_gap_by_date[date]:
            try:
                intraday_df = hist_data_intraday(ticker,date,'FIVE_MINUTE',instrument_list)
                hi_price = intraday_df.iloc[0]['high']
                lo_price = intraday_df.iloc[0]['low']
                open_price = ''
                direction = ''
                date_stats[date][ticker] = 0
                for i in range(1,len(intraday_df[1:])):
                    if intraday_df.iloc[i]["volume"] > 2*(candle_data[ticker].loc[date_orgnl,"avvol"])/75 \
                       and intraday_df.iloc[i]["high"] > hi_price \
                       and open_price == '':
                        open_price = 0.8*intraday_df.iloc[i+1]["open"] + 0.2*intraday_df.iloc[i+1]["high"] #factoring in slippage
                        direction = 'long'
                    elif intraday_df.iloc[i]["volume"] > 2*(candle_data[ticker].loc[date_orgnl,"avvol"])/75 \
                       and intraday_df.iloc[i]["low"] < lo_price \
                       and open_price == '':
                        open_price = 0.8*intraday_df.iloc[i+1]["open"] + 0.2*intraday_df.iloc[i+1]["low"] #factoring in slippage
                        direction = 'short'
                        
                    if open_price != '' and direction == 'long':
                        if intraday_df.iloc[i]["high"] > hi_price*1.05:
                            ticker_return = ((hi_price*1.05)/open_price)-1
                            date_stats[date][ticker] = ticker_return
                            break
                        elif intraday_df.iloc[i]["low"] < lo_price:
                            ticker_return = (lo_price/open_price) - 1
                            date_stats[date][ticker] = ticker_return
                            break
                        else:
                            ticker_return = (intraday_df.iloc[i]["close"]/open_price) - 1
                            date_stats[date][ticker] = ticker_return
                            
                    if open_price != '' and direction == 'short':
                        if intraday_df.iloc[i]["low"] < lo_price*0.95:
                            ticker_return = 1 - ((lo_price*0.95)/open_price)
                            date_stats[date][ticker] = ticker_return
                            break
                        elif intraday_df.iloc[i]["high"] > hi_price:
                            ticker_return = 1 - (hi_price/open_price)
                            date_stats[date][ticker] = ticker_return
                            break
                        else:
                            ticker_return = 1 - (intraday_df.iloc[i]["close"]/open_price)
                            date_stats[date][ticker] = ticker_return
            except:
                print(ticker,date)
                                                 
    return date_stats
                    
date_stats = backtest(top_gap_by_date, candle_data)

###########################KPIs#####################################

def abs_return(date_stats):
    df = pd.DataFrame(date_stats).T
    df["ret"] = df.mean(axis=1)
    df["ret"].fillna(0,inplace=True)
    return (1+df["ret"]).cumprod().iloc[-1] - 1

def win_rate(date_stats):
    win_count = 0
    lose_count = 0
    for i in date_stats:
        for ticker in date_stats[i]:
            if date_stats[i][ticker] > 0:
                win_count+=1
            elif date_stats[i][ticker] < 0:
                lose_count+=1
    return (win_count/(win_count+lose_count))*100
    
def mean_ret_winner(date_stats):
    win_ret = []
    for i in date_stats:
        for ticker in date_stats[i]:
            if date_stats[i][ticker] > 0:
                win_ret.append(date_stats[i][ticker])
    return sum(win_ret)/len(win_ret)

def mean_ret_loser(date_stats):
    los_ret = []
    for i in date_stats:
        for ticker in date_stats[i]:
            if date_stats[i][ticker] < 0:
                los_ret.append(date_stats[i][ticker])
    return sum(los_ret)/len(los_ret)

def equity_curve(date_stats):
    df = pd.DataFrame(date_stats).T
    df["ret"] = df.mean(axis=1)
    df["ret"].fillna(0,inplace=True)
    df["cum_ret"] = (1+df["ret"]).cumprod() - 1
    df["cum_ret"].plot(title="return profile")
    
print("****************Strategy Performance Statistics***************")
print("total cumulative return = {}".format(round(abs_return(date_stats),4)))
print("total win rate = {}".format(round(win_rate(date_stats),2)))
print("mean return per win trade = {}".format(round(mean_ret_winner(date_stats),4)))
print("mean return per loss trade = {}".format(round(mean_ret_loser(date_stats),4)))
equity_curve(date_stats)


