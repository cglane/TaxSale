# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from helpers import LocationFinder
from django.test import TestCase


class UnitTest(TestCase):

    def test_find_info(self):
        """Animals that can speak are correctly identified"""
        address_str = '13 Drews Ct. Charleston SC'
        location_obj = LocationFinder(address_str, '2015')
        location_fields = location_obj.getCensusStats()
        print location_fields
        self.assertEqual(location_fields['Zip'], ' 29403')

