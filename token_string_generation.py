# -*- coding: utf-8 -*-
"""
Angel One - Streaming tick level data

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from smartapi import SmartConnect
from smartapi import SmartWebSocket
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

def stream_list(list_stocks,exchange="nse_cm"):
    #SAMPLE: nse_cm|2885&nse_cm|1594&nse_cm|11536&nse_cm|3045
    # token="mcx_fo|226745&mcx_fo|220822&mcx_fo|227182&mcx_fo|221599"
    return_string = ''
    for count,ticker in enumerate(list_stocks):
        if count != 0:
            return_string+= '&'+exchange+'|'+token_lookup(ticker,instrument_list)
        else:
            return_string+= exchange+'|'+token_lookup(ticker,instrument_list)
    return return_string

token= stream_list(["INFY","HDFC"])  
task="dp"   # mw|sfi|dp

ss = SmartWebSocket(feed_token, key_secret[2])

def on_message(ws, message):
    print("Ticks: {}".format(message))
    
def on_open(ws):
    print("on open")
    ss.subscribe(task,token)
    
def on_error(ws, error):
    print(error)
    

# Assign the callbacks.
ss._on_open = on_open
ss._on_message = on_message
ss._on_error = on_error

ss.connect()




















