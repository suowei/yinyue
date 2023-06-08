from django.core.management.base import BaseCommand
import csv
from yyj.models import Show


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('cast.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                show = Show.objects.get(pk=row[0])
                show.cast.add(row[1])
