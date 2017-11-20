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
        all_docs = Property.objects.all()
        google_finder = GoogleLocationFinder('SC')
        for doc in all_docs:
            address = doc.address
            year = doc.year
            if not doc.census_tract:
                location_obj = LocationFinder(address, year, 'SC')
                location_dict = location_obj.getCensusStats()
                census_tract_record = location_dict.get('census_tract')
                if census_tract_record:
                    doc.census_tract = census_tract_record
                    doc.save()
                    print 'Census Tract added to: %s' % address
                else:

                    close_census_tract = findCloseCensusTracts(google_finder,
                                                               doc.address,
                                                                doc.year,
                                                                   )

                    if close_census_tract:
                        doc.census_tract = close_census_tract
                        doc.save()
                        print 'Close census tract selected: %s' % close_census_tract
                        print 'Close census tract added to : %s' % address
                    else:
                        print 'Exists but still no census tract: %s' % address

        self.stdout.write(self.style.SUCCESS('Successfully finished loop'))