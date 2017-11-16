from django.core.management.base import BaseCommand, CommandError
from properties.models import  CensusTract, Property

class Command(BaseCommand):
    def handle(self, *args, **options):
        ##File Stream
        ##Row Loop

        # for poll_id in options['poll_id']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))