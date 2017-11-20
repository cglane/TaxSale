from django.core.management.base import BaseCommand, CommandError
from properties.models import CensusTract, Property
from properties.helpers import (LocationFinder, GoogleLocationFinder, GovernMaxFinder)
import csv


def findCloseCensusTracts(google_finder, address, year):
    google_finder.getLocation(address)
    zip_code = google_finder.getZipCode()
    town = address.split(',')[-1]

    if zip_code:
        close_property = Property.objects.filter(year=year, zip_code=zip_code, address__icontains=town, census_tract__isnull=False)
    if not zip_code or not close_property:
        close_property = Property.objects.filter(year=year, address__icontains=town, census_tract__isnull=False)
    if close_property:
        return close_property[0].census_tract
class Command(BaseCommand):
    def handle(self, *args, **options):
        filepath = './imports/2014.csv'
        year = '2014'
        reader = csv.DictReader(open(filepath, 'rb'))
        google_finder = GoogleLocationFinder('SC')
        governmax_finder = GovernMaxFinder()
        for test_line in reader:
            pin = test_line['Pin']
            ###To be safe not searching by year
            print pin
            property_records = Property.objects.filter(property_pin=pin)
            if not property_records:
                governmax_data = governmax_finder.getMappedData(pin, year)
                if not all(value == '' for value in governmax_data.values()):
                    address = governmax_data['address']
                    location_obj = LocationFinder(address, year, 'SC')
                    location_dict = location_obj.getCensusStats()
                    location_dict.update(governmax_data)
                    location_dict['year'] = year
                    try:
                        Property.create(location_dict, test_line)
                        print 'Success: %s' % address
                    except Exception as e:
                        print 'Failure: %s' % address
                        print e
                else:
                    'Failed to find data for pin: %s' % pin

            elif not property_records[0].census_tract:
                location_obj = LocationFinder(address, year, 'SC')
                location_dict = location_obj.getCensusStats()
                census_tract_record = location_dict.get('census_tract')
                if census_tract_record:
                    property_records[0].census_tract = census_tract_record
                    property_records[0].save()
                    print 'Census Tract added to: %s' % address
                else:

                    close_census_tract = findCloseCensusTracts(google_finder,
                                                               property_records[0].address,
                                                                property_records[0].year,
                                                                   )

                    if close_census_tract:
                        property_records[0].census_tract = close_census_tract
                        property_records[0].save()
                        print 'Close census tract selected: %s' % close_census_tract
                        print 'Close census tract added to : %s' % address
                    else:
                        print 'Exists but still no census tract: %s' % address
            else:
                address = property_records[0].address
                print "Already added for: %s" % address

        self.stdout.write(self.style.SUCCESS('Successfully finished loop'))