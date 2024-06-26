from django.core.management.base import BaseCommand
import re
import datetime
from yyj.models import Schedule, Artist, MusicalCast, Show


class Command(BaseCommand):
    help = 'Load show cast data.'

    def add_arguments(self, parser):
        parser.add_argument('info', nargs='?', type=str)

    def handle(self, *args, **options):
        s = options['info']
        parts = s.split(",")
        schedule = Schedule.objects.get(id=int(parts[0]))
        numbers = [int(num) for num in re.findall(r'\d+', parts[1])]
        l_numbers = len(numbers)
        if l_numbers == 4:
            month = numbers[0]
            today = datetime.date.today()
            if month < today.month:
                year = today.year + 1
            else:
                year = today.year
            day = numbers[1]
            hour = numbers[2]
            minute = numbers[3]
        elif l_numbers == 5:
            year = numbers[0]
            month = numbers[1]
            day = numbers[2]
            hour = numbers[3]
            minute = numbers[4]
        time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute)
        show = Show.objects.get(schedule=schedule, time=time)
        show.cast_list = show.cast.select_related('role', 'artist')
        artist_a = Artist.objects.get(name=parts[2])
        for cast in show.cast_list:
            if cast.artist == artist_a:
                cast_b = MusicalCast.objects.get(role=cast.role, artist__name=parts[3])
                show.cast.remove(cast)
                show.cast.add(cast_b)
                break
