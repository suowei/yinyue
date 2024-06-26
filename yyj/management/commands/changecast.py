from django.core.management.base import BaseCommand
import re, sys
import datetime
from yyj.models import Schedule, Artist, MusicalCast, Show


class Command(BaseCommand):
    help = 'Change show cast data.'

    def add_arguments(self, parser):
        parser.add_argument('info', nargs='?', type=str)

    def handle(self, *args, **options):
        if not options['info']:
            print("请输入schedule_id:")
            schedule_id = input()
            print("请输入时间:")
            time = input()
            print("请输入原演员:")
            artist_a = input()
            print("请输入现演员:")
            artist_b = input()
        else:
            s = options['info']
            parts = s.split(",")
            schedule_id = parts[0]
            time = parts[1]
            artist_a = parts[2]
            artist_b = parts[3]
        schedule = Schedule.objects.get(id=int(schedule_id))
        numbers = [int(num) for num in re.findall(r'\d+', time)]
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
        artist_a = Artist.objects.get(name=artist_a)
        for cast in show.cast_list:
            if cast.artist == artist_a:
                cast_b = MusicalCast.objects.get(role=cast.role, artist__name=artist_b)
                show.cast.remove(cast)
                show.cast.add(cast_b)
                break
