import configparser
from smartapi import SmartConnect
import pyotp
import time
import pprint
#import yaml

# LOAD CONFIG

parser = configparser.ConfigParser()
parser.read('CONFIG.ini')

API_KEY = parser.get('API_AUTH', 'API_KEY')
CLIENT_ID = parser.get('API_AUTH', 'CLIENT_ID')
EMAIL_ID = parser.get('API_AUTH', 'EMAIL_ID')
PASSWORD =  parser.get('API_AUTH', 'PASSWORD')
MPIN =  parser.get('API_AUTH', 'MPIN')
TOTP_SECURITY_KEY =  parser.get('API_AUTH', 'TOTP_SECURITY_KEY')

# LOAD CONFIG

# LOAD CONFIG
TOTP_OBJ = pyotp.TOTP(TOTP_SECURITY_KEY)
TOTP = TOTP_OBJ.now()

class ANGEL_ONE:
  def __init__(self):
     global API_KEY
     global CLIENT_ID
     global EMAIL_ID
     global PASSWORD
     global MPIN
     global TOTP_SECURITY_KEY
     global TOTP
     self.API_KEY = API_KEY
     self.CLIENT_ID = CLIENT_ID
     self.EMAIL_ID = EMAIL_ID
     self.PASSWORD = PASSWORD
     self.MPIN = MPIN
     self.TOTP_SECURITY_KEY = TOTP_SECURITY_KEY
     self.TOTP = TOTP

  def RETURN_SESSION_OBJ(self):
    self.obj = SmartConnect(api_key=self.API_KEY)
    return self.obj 
  
  def RETURN_SESSION_OBJ_AND_RESPONSE(self):
    self.obj = SmartConnect(api_key=self.API_KEY)
    self.responseSession = self.obj.generateSession(self.CLIENT_ID,self.MPIN,self.TOTP)
    return [self.obj,self.responseSession]
     

# ANGEL_ONE = ANGEL_ONE()
# ANGEL_ONE_OBJ = ANGEL_ONE.RETURN_SESSION_OBJ_AND_RESPONSE()





