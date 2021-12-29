from datetime import datetime
from datetime import date
import requests


from scipy.stats import poisson

a = "qqq"
print(a.__class__.__name__)

# p = poisson.pmf(1, 1.7)
print(poisson.pmf(0, 1.7))
print(poisson.pmf(1, 1.7))
print(poisson.pmf(2, 1.7))
print(poisson.pmf(3, 1.7))
print(poisson.pmf(4, 1.7))
print(poisson.pmf(5, 1.7))


# from bs4 import BeautifulSoup


# a = date(2014, 11, 29)
# b = date(2017, 8 ,30)
# c = (a + (b - a)/2)

# print(c)



# class TstClass():

#     @classmethod
#     def get_or_create(cls):
#         return 'test'

# c = globals().get(None)
# if c:
#     print(c.get_or_create())
# else:
#     print('Empty')

# print(int('71.6'))

# html = open('Countries.html', 'rb').read()
# soup = BeautifulSoup(html, 'html.parser')
# tables = soup.find_all('table')
# table = tables[1]
# s = '{\r'
# for tr in table.select('tr'):
#     tds = tr.select('td')
#     if tds:
#         s += '"' + tds[0].get_text().replace('*','').strip() + '":"' + tds[1].get_text().replace('*','').strip() + '",\r'
# s += '}'
# print(s)


# nationality={
# "Afghanistan":"Afghan",
# "Albania":"Albanian",
# "Algeria":"Algerian",
# "Argentina":"Argentine",
# "Australia":"Australian",
# "Austria":"Austrian",
# "Bangladesh":"Bangladeshi",
# "Belgium":"Belgian",
# "Bolivia":"Bolivian",
# "Botswana":"Batswana",
# "Brazil":"Brazilian",
# "Bulgaria":"Bulgarian",
# "Cambodia":"Cambodian",
# "Cameroon":"Cameroonian",
# "Canada":"Canadian",
# "Chile":"Chilean",
# "China":"Chinese",
# "Colombia":"Colombian",
# "Costa Rica":"Costa Rican",
# "Croatia":"Croatian",
# "Cuba":"Cuban",
# "Czech Republic":"Czech",
# "Denmark":"Danish",
# "Dominican Republic":"Dominican",
# "Ecuador":"Ecuadorian",
# "Egypt":"Egyptian",
# "El Salvador":"Salvadorian",
# "England":"English",
# "Estonia":"Estonian",
# "Ethiopia":"Ethiopian",
# "Fiji":"Fijian",
# "Finland":"Finnish",
# "France":"French",
# "Germany":"German",
# "Ghana":"Ghanaian",
# "Greece":"Greek",
# "Guatemala":"Guatemalan",
# "Haiti":"Haitian",
# "Honduras":"Honduran",
# "Hungary":"Hungarian",
# "Iceland":"Icelandic",
# "India":"Indian",
# "Indonesia":"Indonesian",
# "Iran":"Iranian",
# "Iraq":"Iraqi",
# "Ireland":"Irish",
# "Israel":"Israeli",
# "Italy":"Italian",
# "Jamaica":"Jamaican",
# "Japan":"Japanese",
# "Jordan":"Jordanian",
# "Kenya":"Kenyan",
# "Kuwait":"Kuwaiti",
# "Laos":"Lao",
# "Latvia":"Latvian",
# "Lebanon":"Lebanese",
# "Libya":"Libyan",
# "Lithuania":"Lithuanian",
# "Malaysia":"Malaysian",
# "Mali":"Malian",
# "Malta":"Maltese",
# "Mexico":"Mexican",
# "Mongolia":"Mongolian",
# "Morocco":"Moroccan",
# "Mozambique":"Mozambican",
# "Namibia":"Namibian",
# "Nepal":"Nepalese",
# "Netherlands":"Dutch",
# "New Zealand":"New Zealand",
# "Nicaragua":"Nicaraguan",
# "Nigeria":"Nigerian",
# "Norway":"Norwegian",
# "Pakistan":"Pakistani",
# "Panama":"Panamanian",
# "Paraguay":"Paraguayan",
# "Peru":"Peruvian",
# "Philippines":"Philippine",
# "Poland":"Polish",
# "Portugal":"Portuguese",
# "Romania":"Romanian",
# "Russia":"Russian",
# "Saudi Arabia":"Saudi",
# "Scotland":"Scottish",
# "Senegal":"Senegalese",
# "Serbia":"Serbian",
# "Singapore":"Singaporean",
# "Slovakia":"Slovak",
# "South Africa":"South African",
# "South Korea":"Korean",
# "Spain":"Spanish",
# "Sri Lanka":"Sri Lankan",
# "Sudan":"Sudanese",
# "Sweden":"Swedish",
# "Switzerland":"Swiss",
# "Syria":"Syrian",
# "Taiwan":"Taiwanese",
# "Tajikistan":"Tajikistani",
# "Thailand":"Thai",
# "Tonga":"Tongan",
# "Tunisia":"Tunisian",
# "Turkey":"Turkish",
# "Ukraine":"Ukrainian",
# "United Arab Emirates":"Emirati",
# "(The) United Kingdom":"British",
# "(The) United States":"American",
# "Uruguay":"Uruguayan",
# "Venezuela":"Venezuelan",
# "Vietnam":"Vietnamese",
# "Wales":"Welsh",
# "Zambia":"Zambian",
# "Zimbabwe":"Zimbabwean",
# }