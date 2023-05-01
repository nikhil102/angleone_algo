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

token = "nse_cm|1594&nse_cm|1330" #INFY and HDFC cash equities
task = 'mw' # mw|sfi|dp
ss = SmartWebSocket(feed_token,key_secret[2])

def on_open(ws):
    print("connection opened")
    ss.subscribe(task, token)
    
def on_message(ws, message):
    print(message)
    
def on_error(ws, error):
    print(error)

# Assign the callbacks.
ss._on_open = on_open
ss._on_message = on_message
ss._on_error = on_error

ss.connect()




















