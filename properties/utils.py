import re

def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))

def isNumber(inputString):
    if any(c.isalpha() for c in inputString):
        return False
    return hasNumbers(inputString)


def getVal(opts, csv_dict):
    for key in opts:
        if csv_dict.get(key):
            return formatDictVals(csv_dict[key])
    return None


def formatAddress(addressStr, state):
    """If state not included add, if no number for address use 1"""
    formatted_adddress = "+".join([x for x in addressStr.split()])
    if state not in formatted_adddress:
        formatted_adddress = formatted_adddress + '+' + state
    if not hasNumbers(formatted_adddress):
        formatted_adddress = '1+' + formatted_adddress
    return formatted_adddress


def formatDictVals(val):
    if isinstance(val, str):
        if '$' in val:
            sans_char = val.replace("$", "")
            sans_comma = sans_char.replace(",", "")
            return sans_comma
        if isNumber(val) and ',' in val:
            return val.replace(",", "")
    return val

def stripWhiteSpace(string):
    str_arr = string.split(' ')
    clean_arr = list(filter(None, str_arr))
    return " ".join(clean_arr)


def getListDictNumber(my_list, key, year):
    if isinstance(my_list[0], dict):
        year_keys = [x for x in my_list[0].keys() if 'Year' in x]
        if year_keys:
            ##Get value closest to year
            year_obj = [x for x in my_list if x.get(year_keys[0]) == year]
            if year_obj:
                return formatDictVals(
                    str(
                        year_obj[0].get(key, '0')
                    )
                )
            else:
            ###If year doesn't exist iterate through list
                for itr in my_list:
                    if itr.get(key):
                        return formatDictVals(
                            str(
                                itr[key]
                            )
                        )
                ##If no values exist return 0
                return '0'
        else:
            ###Get highest value
            number_values = [0.0]
            values = [formatDictVals(str(x.get(key, '0'))) for  x in my_list]
            for val in values:
                try:
                    my_float = float(val)
                    number_values.append(my_float)
                except:
                    pass
            return max(number_values)
    return None

def extractData(dictionary, map, year):
    result = {}
    for key, paths in map.iteritems():
        data_source = dictionary
        ## Go down list of keys
        for route in paths:
            if dictionary.get(route):
                data_source = data_source[route]
            else:
                ## If arrive at list find number value
                if isinstance(data_source, list):
                    result[key] = getListDictNumber(data_source, route, year)
                ## If arrive at string set value
                elif isinstance(data_source, dict):
                    result[key] = data_source.get(route)
    return result