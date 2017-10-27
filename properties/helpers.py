import requests
import xmltodict, json
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
from mechanize import Browser, urljoin, urlopen

class CensusTract(object):
  """Queries the census DB for metadata"""
  def __init__(self, addressStr):
    """Get beautiful soup object of the address"""
    formatted_adddress = "+".join([x for x in addressStr.split()])
    tab_url = ("https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address="
            +formatted_adddress
            +"&benchmark=4&vintage=4")
    request = requests.get(tab_url).content
    self.soup = BeautifulSoup(request, 'html.parser')
    self.createDict()

  def createDict(self):
    """Iterates through break tags pulling out the content"""
    census_dict = {}
    results = self.soup.find(id='pl_gov_census_geo_geocoder_domain_AddressResult')
    for br in results.findAll('br'):
      if isinstance(br.nextSibling, NavigableString) and br.nextSibling.nextSibling.name == 'br':
        next_s = br.nextSibling
        if ":" in next_s:
          next_list = next_s.split(':')
          census_dict[next_list[0]] = ''.join(next_list[1::])
      self.census_dict = census_dict
  def getLatLng(self):
    if self.census_dict['Coordinates']:
      split_str = self.census_dict['Coordinates'].split()
      return {'lat': split_str[1], 'lng': split_str[3]}
    return {'lat': '', 'lng': ''}
  def getStats(self):
    landing_page = "https://factfinder.census.gov/faces/nav/jsf/pages/index.xhtml"
    search_box_id = "cfsearchtextboxmain"
    form_id = "cfmainsearchform"
    href_content = "General Population and Housing Characteristics (Population, Age, Sex, Race, Households and Housing, ...)"

    br = Browser()
    br.set_handle_robots(False)
    br.open(landing_page)
    form = next(br.forms())
    form = br.forms[0]
    print(form)
    return {}
    # form["comments"] = "Thanks, Gisle"
    # form.click() returns a mechanize.Request object
    # (see HTMLForm.click.__doc__ if you want to use only the forms support, and
    # not the rest of mechanize)
    # print(urlopen(form.click()).read())      
    ## tr > td[0].content: td[2].content
    # https://factfinder.census.gov/faces/tableservices/jsf/pages/productview.xhtml?pid=ACS_15_5YR_S0601&prodType=table