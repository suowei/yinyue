from django.core.management.base import BaseCommand
import csv
from yyj.models import Show


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('cast.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            show_list = Show.objects.all()
            for show in show_list:
                for cast in show.cast.all():
                    writer.writerow([show.id, cast.musical_cast_id])
