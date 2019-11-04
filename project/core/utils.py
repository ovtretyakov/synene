import datetime
import math
from decimal import Decimal

def get_date_from_string(date_str):
    if not date_str: return None
    try:
        date_str = date_str.replace('"','').replace("'",'')
        if date_str and len(date_str) == 8:
            date_obj = datetime.datetime.strptime(date_str, '%d.%m.%y').date()
        elif date_str and len(date_str) == 10:
            date_obj = datetime.datetime.strptime(date_str, '%d.%m.%Y').date()
        else:
            date_obj = None
    except ValueError as ve:
        date_obj = None
    return date_obj

def get_int(value):
    if value: value = int(value)
    return value

def list_get(l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

def get_match_result(value1, value2):
    '''Return 1,X or 2'''
    if value1==None or value2==None: result = None
    elif value1 > value2: result = '1'
    elif value1 == value2: result = 'X'
    else: result = '2'
    return result

def get_simple_total_over_result(param_value, match_value, odd_value):
    if param_value==None or match_value==None: result=None
    elif param_value < match_value: result = odd_value
    elif param_value == match_value: result = Decimal(1)
    else: result = Decimal(0)
    return result

def get_total_over_result(param_value, match_value, odd_value):
    '''Return total over result taking into account the asian total'''
    param_value = param_value * 2
    param_value1 = math.floor(param_value)
    param_value2 = math.ceil(param_value)
    match_value = match_value * 2
    result = (get_simple_total_over_result(param_value1, match_value, odd_value)/2 +
              get_simple_total_over_result(param_value2, match_value, odd_value)/2)
    return result

def get_simple_total_under_result(param_value, match_value, odd_value):
    if param_value==None or match_value==None: result=None
    elif param_value > match_value: result = odd_value
    elif param_value == match_value: result = Decimal(1)
    else: result = Decimal(0)
    return result

def get_total_under_result(param_value, match_value, odd_value):
    '''Return total under result taking into account the asian total'''
    param_value = param_value * 2
    param_value1 = math.floor(param_value)
    param_value2 = math.ceil(param_value)
    match_value = match_value * 2
    result = (get_simple_total_under_result(param_value1, match_value, odd_value)/2 +
              get_simple_total_under_result(param_value2, match_value, odd_value)/2)
    return result

def get_simple_handicap_result(param_value, match_value, odd_value):
    if param_value==None or match_value==None: result=None
    elif param_value + match_value > 0: result = odd_value
    elif param_value + match_value == 0: result = Decimal(1)
    else: result = Decimal(0)
    return result

def get_handicap_result(param_value, match_value, odd_value):
    '''Return handicap result taking into account the asian handicap'''
    param_value = param_value * 2
    param_value1 = math.floor(param_value)
    param_value2 = math.ceil(param_value)
    match_value = match_value * 2
    result = (get_simple_handicap_result(param_value1, match_value, odd_value)/2 +
              get_simple_handicap_result(param_value2, match_value, odd_value)/2)
    return result
