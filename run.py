from datetime import datetime
from datetime import date

a = date(2014, 11, 29)
b = date(2017, 8 ,30)
c = (a + (b - a)/2)

print(c)



class TstClass():

    @classmethod
    def get_or_create(cls):
        return 'test'

c = globals().get(None)
if c:
    print(c.get_or_create())
else:
    print('Empty')
