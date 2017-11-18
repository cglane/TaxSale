import requests
import xmltodict, json
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
import mechanize
import urllib
from selenium import webdriver
from models import CensusTract
from utils import formatAddress
br = mechanize.Browser()

##Get around robot blocker
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
br.set_handle_robots(False)

class CensusTractHelper(object):
  census_fields = ['B02001_001E', 'B02001_003E', 'B02001_002E']
  census_field_map = {
    'B02001_001E': 'population_total',
    'B02001_003E': 'black_total',
    'B02001_002E': 'white_total',
    'county': 'county',
    'tract': 'tract_number',
    'state': 'state'
  }
  demo_query = "https://api.census.gov/data/{0}/acs5?get={1}&for=tract:{2}&in=state:{3}%20county:{4}&key={5}"
  census_map = getattr(settings, 'CENSUS_MAP')
  census_key = getattr(settings, 'CENSUS_KEY')
  ##Static values for South Carolina and Charleston County

  state_id=census_map.get('SC')
  county_id=census_map.get('Charleston County')

  def getTractId(self, tract, year):
    data_year = self.allowedYear(year)
    census_tract = CensusTract.filter(year=data_year, tract=tract)
    if census_tract:
      return census_tract.id
    else:
      return self.getTractDemo(tract, year)
  def allowedYear(self, year):
    """Census data only goes to 2015"""
    year_max = getattr(settings, 'YEAR_MAX')
    if int(year) > year_max:
      return year_max
    return year
  def getTractDemo(self, tract, year):
    fields = ','.join(self.census_fields)
    data_year = self.allowedYear(year)
    my_query = self.demo_query.format(data_year, fields, tract, self.state_id, self.county_id, self.census_key)
    response = requests.get(my_query)
    if response.status_code == 200:
      tract = CensusTract.create(response, self.census_field_map, data_year)
      return tract.id
    return 2


class LocationFinder(CensusTractHelper):
  """Queries the census DB for metadata"""
  geo_fields = ['Lat', 'Lng', 'TRACT', 'Zip']
  def __init__(self, addressStr, year, state):
    """Get beautiful soup object of the address"""
    self.year = year
    formatted_address = formatAddress(addressStr, state)

    print (formatted_adddress, 'formatted address')
    tab_url = ("https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?a"
            +"?address="
            +formatted_adddress
            +"&benchmark=4&vintage=4")
    print ('tab_url', tab_url)
    request = requests.get(tab_url).content
    self.soup = BeautifulSoup(request, 'html.parser')
    print self.soup
    self.createLocationDict()
    self.getLatLng()

  def createLocationDict(self):
    """Iterates through break tags pulling out the content"""
    census_dict = {}
    results = self.soup.find(id='pl_gov_census_geo_geocoder_domain_AddressResult')
    if results:
      for br in results.findAll('br'):
        if isinstance(br.nextSibling, NavigableString) and br.nextSibling.nextSibling.name == 'br':
          next_s = br.nextSibling
          if ":" in next_s:
            next_list = next_s.split(':')
            census_dict[next_list[0]] = ''.join(next_list[1::])
        self.location_dict = census_dict
    else:
      self.location_dict = {}

  def getLatLng(self):
    if self.location_dict.get('Coordinates'):
      split_str = self.location_dict['Coordinates'].split()
      self.location_dict['Lat'] = split_str[1]
      self.location_dict['Lng'] = split_str[3]
    else:
      self.location_dict['Lat'] = ''
      self.location_dict['Lng'] = ''

  def getCensusStats(self):
    """Using Census tract use acs5 to get demographic data per year use cache if it exists"""
    census_tract_id = self.location_dict.get('TRACT')
    if census_tract_id:
      census_tract_record = self.getTractDemo(census_tract_id, self.year)
      location_fields = { field: self.location_dict[field] for field in self.geo_fields }
      location_fields['census_tract'] = census_tract_record
      return location_fields
    return { field: '' for field in self.geo_fields }

