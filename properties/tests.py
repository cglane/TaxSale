# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from helpers import LocationFinder
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

