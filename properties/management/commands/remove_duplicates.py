from django.core.management.base import BaseCommand, CommandError
from properties.models import CensusTract, Property

class Command(BaseCommand):
    def handle(self, *args, **options):
        for row in Property.objects.all():

            if Property.objects.filter(property_pin=row.property_pin, year=row.year).count() > 1:
                row.delete()
                print 'Row deleted for address %s' % row.address