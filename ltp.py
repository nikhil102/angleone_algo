# -*- coding: utf-8 -*-
"""
Angel One - get last traded price of any ticker

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
        
def get_ltp(instrument_list,ticker,exchange="NSE"):
    params = {
                "tradingsymbol":"{}-EQ".format(ticker),
                "symboltoken": token_lookup(ticker, instrument_list)
             }
    response = obj.ltpData(exchange, params["tradingsymbol"], params["symboltoken"])
    return response["data"]["ltp"]



ltp = get_ltp(instrument_list,"HCLTECH")














