from django.core.management.base import BaseCommand
import csv
import datetime
from django.utils import timezone
from yyj.models import Show


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='?')
        parser.add_argument('month', nargs='?')

    def handle(self, *args, **options):
        year = int(options['year'])
        month = int(options['month'])
        begin = datetime.date(year, month, 1)
        if month != 12:
            end = datetime.date(year, month + 1, 1)
        else:
            end = datetime.date(year + 1, 1, 1)
        show_list = Show.objects.filter(time__range=(begin, end)).select_related(
            'schedule', 'schedule__tour', 'schedule__tour__musical',
            'schedule__stage', 'schedule__stage__theatre', 'schedule__stage__theatre__city'
        ).order_by('schedule__stage__theatre__city__seq', 'time')
        filename = 'download/' + options['year'] + options['month'] + '.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['时间', '城市', '音乐剧', '卡司', '剧院'])
            for show in show_list:
                value_list = show.cast.select_related('role', 'artist').values_list(
                    'artist__name', flat=True).order_by('role__seq')
                cast_string = ' '.join(value_list)
                writer.writerow([
                    timezone.localtime(show.time).strftime("%Y-%m-%d %H:%M"),
                    show.schedule.stage.theatre.city.name,
                    show.schedule.tour.musical.name,
                    cast_string,
                    show.schedule.stage.__str__(),
                ])
        print(show_list.count())
