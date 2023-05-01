from smartapi import SmartConnect
import pyotp
import time

CONFIG = {
    "API_KEY" : 'ZZ6CRqGZ',
    "CLIENT_ID" : 'SAHW1028',
    "EMAIL_ID" : 'shindenikhil102@gmail.com',
    "PASSWORD" : 'Mastermind@123',
    "MPIN" : '2525',
    "TOTP_SECURITY_KEY" : "MALBI3B35CGKNABT6LJE62SKUY"
    }

globals().update(CONFIG)
totp_obj = pyotp.TOTP(TOTP_SECURITY_KEY)
totp = totp_obj.now()
obj=SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_ID,MPIN,totp)
print(data)
