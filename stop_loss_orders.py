# -*- coding: utf-8 -*-
"""
Angel One - placing stop loss basics

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
import os
import urllib
import json
from pyotp import TOTP

key_path = r"D:\OneDrive\Udemy\Angel One API"
os.chdir(key_path)

key_secret = open("key.txt","r").read().split()

obj=SmartConnect(api_key=key_secret[0])
data = obj.generateSession(key_secret[2],key_secret[3],TOTP(key_secret[4]).now())
feed_token = obj.getfeedToken()

instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = urllib.request.urlopen(instrument_url)
instrument_list = json.loads(response.read())

def token_lookup(ticker, instrument_list, exchange="NSE"):
    for instrument in instrument_list:
        if instrument["name"] == ticker and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[-1] == "EQ":
            return instrument["token"]

def place_sl_limit_order(instrument_list,ticker,buy_sell,price,quantity,exchange="NSE"):
    params = {
                "variety":"STOPLOSS",
                "tradingsymbol":"{}-EQ".format(ticker),
                "symboltoken":token_lookup(ticker, instrument_list),
                "transactiontype":buy_sell,
                "exchange":exchange,
                "ordertype":"STOPLOSS_LIMIT",
                "producttype":"INTRADAY",
                "duration":"DAY",
                "price":price+0.05,
                "triggerprice":price,
                "quantity":quantity
                }
    response = obj.placeOrder(params)
    return response

def place_sl_market_order(instrument_list,ticker,buy_sell,price,quantity,sl=0,sqof=0,exchange="NSE"):
    params = {
                "variety":"STOPLOSS",
                "tradingsymbol":"{}-EQ".format(ticker),
                "symboltoken":token_lookup(ticker, instrument_list),
                "transactiontype":buy_sell,
                "exchange":exchange,
                "ordertype":"STOPLOSS_MARKET",
                "producttype":"INTRADAY",
                "duration":"DAY",
                "triggerprice":price,
                "price":price,
                "quantity":quantity
                }
    response = obj.placeOrder(params)
    return response


place_sl_limit_order(instrument_list, "HCLTECH", "BUY", 980, 1) #price needs to be greater than LTP for buy orders
place_sl_market_order(instrument_list, "HCLTECH", "BUY", 980, 1) #price needs to be greater than LTP for buy orders














