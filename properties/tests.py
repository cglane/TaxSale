# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from helpers import (LocationFinder, GovernMaxFinder, GoogleLocationFinder)
from django.test import TestCase
import csv
from models import Property
class UnitTest(TestCase):

    def test_find_info(self):
        """Animals that can speak are correctly identified"""
        address_str = '13 Drews Ct. Charleston SC'
        location_obj = LocationFinder(address_str, '2015', 'SC')
        location_fields = location_obj.getCensusStats()
        self.assertEqual(location_fields['Zip'], ' 29403')

    def test_read_file_query(self):
        filepath = './data-all.csv'
        reader = csv.DictReader(open(filepath, 'rb'))
        for test_line in list(reader)[0:5]:
            address = test_line['Parcel Address']
            year = test_line['TaxYear']

            location_obj = LocationFinder(address, year, 'SC')
            location_dict = location_obj.getCensusStats()

            property = Property.create(location_dict, test_line)
            self.assertEqual(test_line['Parcel Address'], property.address)

    def setUp(self):
        prop_dict = {
            'year': '2017',
            'address': "13 Drews Ct, SC",
            'property_pin':'4590501053',
            'zip_code': '29403',
            'property_value': '20000',
            'status': 'DEED',
            'acreage': 0
        }
        prop = Property(**prop_dict)
        prop.save()
    def test_get_dict_governmax_land(self):
        governmax = GovernMaxFinder()
        mapped_data = governmax.getMappedData('7640000227', '2015')
        self.assertEqual(str(mapped_data['property_value']), str('6000'))

    def test_get_dict_governmax_structure(self):
        governmax = GovernMaxFinder()
        mapped_data = governmax.getMappedData('4590501053', '2017')
        props = Property.objects.filter(property_pin='4590501053')
        Property.objects.filter(id=props[0].id).update(**mapped_data)
        props = Property.objects.filter(property_pin='4590501053')
        new_props = props[0]
        self.assertEqual(new_props.year, 2017)
        self.assertEqual(new_props.property_value, 110000)

    def test_get_dict_governmax_bad_key(self):
        governmax = GovernMaxFinder()
        mapped_data = governmax.getMappedData('764000027', '2015')
        self.assertEqual(mapped_data['property_value'], '' )

    def test_google_zipcode(self):
        google_finder = GoogleLocationFinder('SC')
        google_finder.getLocation('LUCKY RD, CHARLESTON')
        zip_code = google_finder.getZipCode()
        self.assertEqual(zip_code, '29412')