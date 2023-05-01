# -*- coding: utf-8 -*-
"""
Angel One - modifying orders

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

def place_limit_order(instrument_list,ticker,buy_sell,price,quantity,exchange="NSE"):
    params = {
                "variety":"NORMAL",
                "tradingsymbol":"{}-EQ".format(ticker),
                "symboltoken":token_lookup(ticker, instrument_list),
                "transactiontype":buy_sell,
                "exchange":exchange,
                "ordertype":"LIMIT",
                "producttype":"INTRADAY",
                "duration":"DAY",
                "price":price,
                "quantity":quantity
                }
    response = obj.placeOrder(params)
    return response


order_id = place_limit_order(instrument_list, "AXISBANK", "BUY", 750, 1)

##############
def modify_limit_order(instrument_list,ticker,order_id,price,quantity):
    params = {
                "variety":"NORMAL",
                "orderid":order_id,
                "ordertype":"LIMIT",
                "producttype":"INTRADAY",
                "duration":"DAY",
                "price":price,
                "quantity":quantity,
                "tradingsymbol":"{}-EQ".format(ticker),
                "symboltoken":token_lookup(ticker, instrument_list),
                "exchange":"NSE"
                }
    response = obj.modifyOrder(params)
    return response

modify_limit_order(instrument_list,"AXISBANK",order_id,760,2) #changing both price and quantity of open orders

#################
def modify_order_type(instrument_list,ticker,order_id,order_type,quantity):
    params = {
                "variety":"NORMAL",
                "orderid":order_id,
                "ordertype":order_type,
                "producttype":"INTRADAY",
                "duration":"DAY",
                "tradingsymbol":"{}-EQ".format(ticker),
                "quantity":quantity,
                "symboltoken":token_lookup(ticker, instrument_list),
                "exchange":"NSE"
                }
    response = obj.modifyOrder(params)
    return response

modify_order_type(instrument_list,"AXISBANK",order_id,"MARKET",1)













