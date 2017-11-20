import requests
import xmltodict, json
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
import mechanize
import urllib
from selenium import webdriver
from models import CensusTract
from utils import (formatAddress, stripWhiteSpace, extractData)
br = mechanize.Browser()

###For Development
import pprint
pp = pprint.PrettyPrinter(indent=4)

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

  def getTract(self, tract, year):
    data_year = self.allowedYear(year)
    census_tract = CensusTract.objects.filter(year=data_year, tract_number=tract)
    if not tract:
      return None
    if census_tract:
      return census_tract[0]
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
      return tract
    return None


class LocationFinder(CensusTractHelper):
  """Queries the census DB for metadata"""
  geo_fields = ['Lat', 'Lng', 'TRACT', 'Zip']
  def __init__(self, addressStr, year, state):
    """Get beautiful soup object of the address"""
    self.year = year
    formatted_address = formatAddress(addressStr, state)

    tab_url = ("https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
            +"?address="
            +formatted_address
            +"&benchmark=4&vintage=4")
    request = requests.get(tab_url).content
    self.soup = BeautifulSoup(request, 'html.parser')
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
      census_tract_record = self.getTract(census_tract_id, self.year)
      location_fields = { field: self.location_dict[field] for field in self.geo_fields }
      location_fields['census_tract'] = census_tract_record
      return location_fields
    return { field: '' for field in self.geo_fields }

class GoogleLocationFinder(object):
  """Query google for location information, if census is not working"""
  google_api_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'
  def __init__(self, state_abbrev):
    self.api_key = getattr(settings, 'GOOGLE_API_KEY')
    self.state_abbrev = state_abbrev
  def getLocation(self, address):
    """Getting result from google and making sure it is in the right state at least"""
    address_formatted = "+".join(address.split(' '))
    request_url = self.google_api_url.format(address_formatted, self.api_key)
    google_response = json.loads(requests.get(request_url).content)
    if google_response['status'] == 'OK':
      in_state_results = []
      for result in google_response['results']:
        short_names = [x['short_name'] for x in result['address_components']]
        if self.state_abbrev in short_names:
          in_state_results.append(result)
      self.results = in_state_results
      return in_state_results
    else:
      self.results = None
      return None
  def getZipCode(self):
    """Iterating through results looking for a postal_code entry"""
    if self.results:
      for result in self.results:
        zip_code_dict = [x for x in result['address_components'] if 'postal_code' in x['types']]
        if zip_code_dict:
          return zip_code_dict[0]['short_name']
    return None

class GovernMaxFinder(object):
  """Query Governmax Website for Information about the property in question"""
  governmax_query_url = 'http://sc-charleston-county.governmax.com/svc/tab_summary_report_SC-Char.asp?t_nm=summary&l_cr=1&t_wc=|parcelid={0}+++++++++++++++&sid={1}'
  api_key_url = 'http://sc-charleston-county.governmax.com/svc/'
  data_map = {
    'address': ('overview', 'Parcel Address'),
    'finished_sq_feet' : ('improvements', 'Finished Sq. Ft.',),
    'highest_sales_price': ('sales_history', 'Sale Price',),
    'property_value': ('historic_info', 'Market',),
    'property_class_code': ('current_info','Property Class Code',),
    'acreage': ('current_info', 'Acreage',),
    'bedrooms': ('improvements', 'Bedrooms',),
    'constructed_year': ('improvements', 'Constructed Year',),
  }
  def __init__(self):
    ##Get API Key
    self.getApiKey()

  def  getApiKey(self):
    req = requests.get(self.api_key_url).content
    soup = BeautifulSoup(req, 'html.parser')
    frames = soup.find_all('frame')
    frame_src = frames[0]['src']
    api_key = frame_src.split('sid=')[1].split('&agencyid=')[0]
    self.api_key = api_key
    return api_key

  def getSoup(self, property_pin):
    request_url = self.governmax_query_url.format(property_pin, self.api_key)
    request = requests.get(request_url).content
    soup = BeautifulSoup(request, 'html.parser')
    return soup

  def getRawData(self, property_pin):
    soup = self.getSoup(property_pin)
    if soup and soup.findAll('table'):
      self.tables = soup.findAll('table')[2].findAll('table')[5].findAll('table')
      all_tr = self.tables[0].findAll('tr')
      ## If all_tr empty property not found
      if self.tables and all_tr:
        dictionary_info = {
          'overview': self.getOverview(),
          'current_info': self.getCurrentParcelInfo(),
          'historic_info': self.getHistoricInformation(),
          'sales_history': self.getSalesDisclosure(),
          'improvements': self.getImprovements()
        }

        return dictionary_info
    return {key: '' for key in self.data_map.keys()}



  def getMappedData(self, property_pin, year):
    dictionary_info = self.getRawData(property_pin)
    ### If dict vals all empty return as is
    if all(value == '' for value in dictionary_info.values()):
      return dictionary_info
    ### Extract data from massive dict per util definition
    return extractData(dictionary_info, self.data_map, year)

  def getOverview(self):
    """Gets overview table from governmax as dictionary"""
    first_table = self.tables[0]
    all_tr = first_table.findAll('tr')
    first_header = [x.get_text('', strip=True) for x in all_tr[0].findAll('span')]
    first_header_data = [x.get_text('', strip=True) for x in all_tr[1].findAll('span')]
    return dict(zip(first_header, first_header_data))

  def getCurrentParcelInfo(self):
    """Gets data from 'Current Parcel Information' table."""
    'Second Table'
    owner_class_table = self.tables[3]
    owner_values_fields = [stripWhiteSpace(x.get_text('', strip=True)) for x in owner_class_table.findAll('font')]
    owner_dict = dict(zip(*[iter(owner_values_fields)] * 2))
    'Fourth Class'
    property_info_table = self.tables[4]
    property_fields_values = [stripWhiteSpace(x.get_text('', strip=True)) for x in property_info_table.findAll('font')]
    property_class_dict = dict(zip(*[iter(property_fields_values)] * 2))
    ##Merge two dicts
    owner_dict.update(property_class_dict)
    return owner_dict

  def getHistoricInformation(self):
    """This gets historic information table as array of dictionaries."""
    historic_info_table = self.tables[7]
    historic_fields = [x.get_text('', strip=True) for x in historic_info_table.findAll("span", class_="datalabel")]
    historic_data = historic_info_table.findAll('tr')[1:]
    historic_info_list = [[stripWhiteSpace(p.get_text('', strip=True)) for p in x.findAll('span')] for x in
                          historic_data]
    if historic_info_list:
      return [dict(zip(historic_fields, x)) for x in historic_info_list]

    return [dict.fromkeys(historic_fields)]

  def getSalesDisclosure(self):
    """This gets sales disclosure table as array of dictionaries."""
    sales_disclosure_table = self.tables[9]
    sales_disclosure_fields = [x.get_text('', strip=True) for x in
                               sales_disclosure_table.findAll("span", class_="datalabel")]
    sales_disclosure_data = sales_disclosure_table.findAll('tr')[1:]
    sales_disclosure_info_list = [[stripWhiteSpace(p.get_text('', strip=True)) for p in x.findAll('font')] for x in
                                  sales_disclosure_data]
    if sales_disclosure_info_list:
      return [dict(zip(sales_disclosure_fields, x)) for x in sales_disclosure_info_list]
    return [dict.fromkeys(sales_disclosure_fields)]

  def getImprovements(self):
    """Get improvements table as dictionary"""
    improvements_table = self.tables[10]
    improvements_fields = [x.get_text('', strip=True) for x in improvements_table.findAll("span", class_="datalabel")]
    improvements_data = improvements_table.findAll('tr')[2:]
    improvements_values = [[stripWhiteSpace(p.get_text('', strip=True)) for p in x.findAll('font')] for x in
                           improvements_data]
    if (len(improvements_values) > 0):
      return [dict(zip(improvements_fields, x)) for x in improvements_values]
    return [dict.fromkeys(improvements_fields)]