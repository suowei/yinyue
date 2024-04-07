from django.core.management.base import BaseCommand
import csv
from yyj.models import Schedule, Role, MusicalCast, Show


class Command(BaseCommand):
    help = 'Load show cast data.'

    def add_arguments(self, parser):
        parser.add_argument('schedule_id', nargs='?')

    def handle(self, *args, **options):
        pk = int(options['schedule_id'])
        schedule = Schedule.objects.get(pk=pk)
        role_list = Role.objects.filter(musical=schedule.tour.musical).order_by('seq')
        musical_cast_list = MusicalCast.objects.filter(role__musical=schedule.tour.musical).select_related('role', 'artist')
        role_id_list = []
        filename = options['schedule_id'] + '.csv'
        with open(filename, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == '角色':
                    for s_role in row[1:]:
                        for role in role_list:
                            if s_role == role.name:
                                role_id_list.append(role)
                                break
                else:
                    show, created = Show.objects.get_or_create(schedule=schedule, time=row[0])
                    for i, s_artist in enumerate(row[1:]):
                        for musical_cast in musical_cast_list:
                            if musical_cast.role == role_id_list[i] and musical_cast.artist.name == s_artist:
                                show.cast.add(musical_cast)
                                break
