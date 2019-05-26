
def get_int(value):
    if value: value = int(value)
    return value

def get_match_result(value1, value2):
    '''Return 1,X or 2'''
    if value1==None or value2==None: result = None
    elif value1 > value2: result = '1'
    elif value1 == value2: result = 'X'
    else: result = '2'
    return result
