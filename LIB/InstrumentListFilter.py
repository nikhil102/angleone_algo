##########################################################################
def checkwithcurrentobject(param_key,param_value, instrument):
    valcheck = instrument.get(param_key)
    if valcheck is not None:
        if valcheck == param_value:
           return instrument
    return None

def equal_str(param_key,param_value, instrument_list,Record='Single'):
    if param_value == "":
       return None
    if type(param_value) != "str":
       param_value = str(param_value)
    
    R = []
    for instrument in instrument_list:
        re = checkwithcurrentobject(param_key,param_value,instrument)
        if Record == 'Single':
            if re != None:
              return re 
        else:
            if re != None:
              R.append(instrument.copy())
            
    if Record == 'Single':
        return None
    else:
        return R

def match_str(param_key,param_value, instrument_list, dir ="ANY"):
    if param_value == "":
       return None
    if type(param_value) != "str":
       param_value = str(param_value)

    R = []
    for instrument in instrument_list:
        valcheck = instrument.get(param_key)
        if valcheck is not None:
           txt = instrument[param_key]
           if dir == "ANY" or dir == "Any" or dir == "any":
                if txt.find(param_value) >= 0 :
                    R.append(instrument.copy())
           elif dir == "START" or dir == "Start" or dir == "start":
                if txt.startswith(param_value):
                    R.append(instrument.copy())
           elif dir == "END" or dir == "End"  or dir == "end":
                if txt.endswith(param_value):
                    R.append(instrument.copy())
               
    return R



#####################################################

def FindByToken(token, instrument_list):
    return equal_str("token",token,instrument_list)

#####################################################
def FindBySymbol(symbol, instrument_list):
    return equal_str("symbol",symbol,instrument_list)

def FindBySymbol_multiple_result(symbol, instrument_list):
    return equal_str("symbol",symbol,instrument_list,'MULTIPLE')

def FindBySymbol_Match(symbol, instrument_list):
    return match_str("symbol",symbol,instrument_list,"any")

#####################################################

def FindByName(name, instrument_list):
    return equal_str("name",name,instrument_list)

def FindByName_multiple_result(name, instrument_list):
    return equal_str("name",name,instrument_list,'MULTIPLE')

#####################################################

def FindByExpirydate(expiry, instrument_list):
    return equal_str("expiry",expiry,instrument_list)

def FindByExpirydate_multiple_result(expiry, instrument_list):
    return equal_str("expiry",expiry,instrument_list,'MULTIPLE')

def FindByExpirydate_Match(expiry, instrument_list):
    return match_str("expiry",expiry,instrument_list,"any")

def FindByExpirydate_Match_from_left(expiry, instrument_list):
    return match_str("expiry",expiry,instrument_list,"start")

def FindByExpirydate_Match_from_Right(expiry, instrument_list):
    return match_str("expiry",expiry,instrument_list,"end")

#####################################################