from django.core.management.base import BaseCommand
import csv
from yyj.models import Theatre, Location


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('theatre_location.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                theatre = Theatre.objects.get(name=row[0])
                location = Location.objects.get(name=row[1])
                theatre.location = location
                theatre.save()
