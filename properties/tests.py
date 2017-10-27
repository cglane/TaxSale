# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from helpers import CensusTract

class TestCensusTract(unittest.TestCase):
    def test_get_census_tract(self):
        """Find Soup info from address string"""
        address_str = '13 Drews Ct. Charleston SC'
        soup = CensusTract(address_str)
        lat_lng = soup.getLatLng()
        self.assertEqual(lat_lng['lat'], '-79.94081')
    def test_get_stats(self):
        address_str = '13 Drews Ct. Charleston SC'
        soup = CensusTract(address_str)
        stats = soup.getStats()
        self.assertEqual(stats, {})
if __name__ == '__main__':
    unittest.main()