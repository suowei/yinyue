from django.core.management.base import BaseCommand
import datetime
from yyj.models import Schedule, Role, MusicalCast, Show


class Command(BaseCommand):
    help = 'Check schedule cast data.'

    def add_arguments(self, parser):
        parser.add_argument('schedule_id', nargs='?')

    def handle(self, *args, **options):
        pk = int(options['schedule_id'])
        schedule = Schedule.objects.get(pk=pk)
        now = datetime.datetime.now()
        schedule.shows = schedule.show_set.filter(time__gte=now)
        for show in schedule.shows:
            show_cast_list = show.cast.select_related('artist')
            if not show_cast_list:
                continue
            for show_cast in show_cast_list:
                show_count = Show.objects.filter(cast__artist=show_cast.artist_id, time=show.time).distinct().count()
                if show_count > 1:
                    print(show_cast.artist_id, show.time)
