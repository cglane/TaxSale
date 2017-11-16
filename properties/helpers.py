import requests
import xmltodict, json
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
import mechanize
import urllib
from selenium import webdriver
from models import CensusTract
br = mechanize.Browser()
##Get around robot blocker
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
br.set_handle_robots(False)

class CensusTract(object):
  census_field_map = {
    'B00001_001E': 'total',
    'B06012_002E': 'below_100_poverty',
    'B01001B_001E': 'black_total',
    'B01001H_001E': 'white_total',
    'B01001H_001E': 'hispanic_total'
  }
  demo_query = "https://api.census.gov/data/{0}/acs5?get={1}&for=tract:{2}"

  def getTractId(self, tract, year):
    census_tract = CensusTract.filter(year=year, tract=tract)
    if census_tract:
      return census_tract.id
    else:
      return self.getCensusTract(tract, year)

  def getTractDemo(self, tract, year):
    pass


class LocationFinder(CensusTract):
  """Queries the census DB for metadata"""
  geo_fields = ['Lat', 'Lng', 'Tract', 'Zip', 'Address']
  def __init__(self, addressStr, year):
    """Get beautiful soup object of the address"""
    self.year = year
    formatted_adddress = "+".join([x for x in addressStr.split()])
    tab_url = ("https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address="
            +formatted_adddress
            +"&benchmark=4&vintage=4")
    request = requests.get(tab_url).content
    self.soup = BeautifulSoup(request, 'html.parser')
    self.createLocationDict()
    self.getLatLng()

  def createLocationDict(self):
    """Iterates through break tags pulling out the content"""
    census_dict = {}
    results = self.soup.find(id='pl_gov_census_geo_geocoder_domain_AddressResult')
    for br in results.findAll('br'):
      if isinstance(br.nextSibling, NavigableString) and br.nextSibling.nextSibling.name == 'br':
        next_s = br.nextSibling
        if ":" in next_s:
          next_list = next_s.split(':')
          census_dict[next_list[0]] = ''.join(next_list[1::])
      self.location_dict = census_dict

  def getLatLng(self):
    if self.census_dict['Coordinates']:
      split_str = self.census_dict['Coordinates'].split()
      self.location_dict['Lat'] = split_str[1]
      self.location_dict['Lng'] = split_str[3]
    else:
      self.location_dict['Lat'] = ''
      self.location_dict['Lng'] = ''

  def getCensusStats(self):
    """Using Census tract use acs5 to get demographic data per year use cache if it exists"""
    # Query cache
    # Try Catch
    # Query based on tract number
    # Apply Varibable list
    # Convert to Dict based on Variables Map
    # Set Cache
    census_tract_id = self.location_dict['Tract']
    if census_tract_id:
      census_tract_record = self.getTractDemo(census_tract_id, self.year)
      location_fields = { field: self.location_dict[field] for field in geo_fields }
      location_fields['']
    return {}