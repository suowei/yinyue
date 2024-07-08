from django.core.management.base import BaseCommand
import csv
from yyj.models import Location


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('location.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Location.objects.get_or_create(seq=row[0], name=row[1], longitude=row[2], latitude=row[3])
