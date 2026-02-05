from django.core.management.base import BaseCommand
import datetime
from yyj.models import Schedule, MusicalCast, Show


class Command(BaseCommand):
    help = 'Replace cast in a specific show at a given schedule_id and show_time'

    def add_arguments(self, parser):
        parser.add_argument('schedule_id', type=int, help='The schedule ID')
        parser.add_argument('show_time', type=str, help="The show time in 'YYYY-MM-DD HH:MM' format")
        parser.add_argument('original_cast', type=str, help='The name of the original cast member')
        parser.add_argument('new_cast', type=str, help='The name of the new cast member')

    def handle(self, *args, **options):
        schedule_id = options['schedule_id']
        show_time_str = options['show_time']
        original_cast_name = options['original_cast']
        new_cast_name = options['new_cast']

        # 将 show_time 字符串转为 datetime 对象
        try:
            show_time = datetime.datetime.strptime(show_time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid show time format. Please use 'YYYY-MM-DD HH:MM'.")
            return

        # 获取 Schedule 对象
        try:
            schedule = Schedule.objects.get(pk=schedule_id)
        except Schedule.DoesNotExist:
            print("Schedule does not exist.")
            return

        # 获取 Show 对象
        try:
            show = Show.objects.get(schedule=schedule, time=show_time)
        except Show.DoesNotExist:
            print("Show does not exist.")
            return

        # 替换卡司
        show.cast_list = show.cast.select_related('role', 'artist')
        for cast in show.cast_list:
            if cast.artist.name == original_cast_name:
                try:
                    new_cast = MusicalCast.objects.get(role=cast.role, artist__name=new_cast_name)
                except MusicalCast.DoesNotExist:
                    print("New cast {new_cast_name} not found.")
                    return
                show.cast.remove(cast)
                show.cast.add(new_cast)
                print("Successfully replaced.")
                break
        else:
            print("Original cast is not in the show.")
