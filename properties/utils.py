import re

def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))

def getVal(opts, csv_dict):
    for key in opts:
        if csv_dict.get(key):
            return formatDictVals(key, csv_dict[key])
    return None
def formatAddress(addressStr, state):
    """If state not included add, if no number for address use 1"""
    formatted_adddress = "+".join([x for x in addressStr.split()])
    if state not in formatted_adddress:
        formatted_adddress = formatted_adddress + '+' + state
    if not hasNumbers(formatted_adddress):
        formatted_adddress = '1' + formatted_adddress
    return formatted_adddress

def formatDictVals(key, val):
    if '$' in val:
        sans_char = val.replace("$", "")
        sans_comma = sans_char.replace(",", "")
        return sans_comma
    if key == 'Status':
        return val == 'DEED'
    if ',' in val:
        return val.replace(",", "")
    return val
