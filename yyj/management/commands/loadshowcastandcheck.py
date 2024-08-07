from django.core.management.base import BaseCommand
import re, glob
import datetime
from yyj.models import Schedule, Role, MusicalCast, Show, Conflict


class Command(BaseCommand):
    help = 'Load show cast data and check.'

    def add_arguments(self, parser):
        parser.add_argument('schedule_id', nargs='?')

        parser.add_argument('--first',
                            action='store_true',
                            help='Load all txt.',
                            )

    def handle(self, *args, **options):
        if options['first']:
            txt_files = glob.glob('*.txt')
            txt_file = txt_files[0]
            schedule_id = txt_file.split('.')[0]
            print(schedule_id)
        else:
            if not options['schedule_id']:
                print('请输入schedule_id:')
                schedule_id = input()
            else:
                schedule_id = options['schedule_id']
        schedule = Schedule.objects.get(pk=int(schedule_id))
        role_list = Role.objects.filter(musical=schedule.tour.musical).order_by('seq')
        musical_cast_list = MusicalCast.objects.filter(
            role__musical=schedule.tour.musical).select_related('role', 'artist')
        filename = schedule_id + '.txt'
        with open(filename, encoding="utf-8") as f:
            # 读取角色列表
            line = f.readline()
            row = line.split('\t')
            role_id_list = []
            if row[0] == '角色':
                for s_role in row[1:]:
                    for role in role_list:
                        if s_role.strip() == role.name:
                            role_id_list.append(role)
                            break
            # 读取每一场演出的卡司排期并检查演员行程是否冲突
            today = datetime.date.today()
            while line:
                line = f.readline()
                row = line.split('\t')
                # 去除空格和换行符
                row = [s.strip() for s in row]
                row = [s for s in row if s]
                # 读取日期和时间并添加演出信息
                for i, s in enumerate(row):
                    numbers = [int(num) for num in re.findall(r'\d+', row[i])]
                    l_numbers = len(numbers)
                    # 如果有冒号代表读取结束
                    if ':' in row[i]:
                        if l_numbers == 2:
                            hour = numbers[0]
                            minute = numbers[1]
                        elif l_numbers == 4:
                            month = numbers[0]
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
                        break
                    # 如果没有冒号只读取日期
                    if l_numbers == 2:
                        month = numbers[0]
                        if month < today.month:
                            year = today.year + 1
                        else:
                            year = today.year
                        day = numbers[1]
                    elif l_numbers == 3:
                        year = numbers[0]
                        month = numbers[1]
                        day = numbers[2]
                time = str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute)
                show, created = Show.objects.get_or_create(schedule=schedule, time=time)
                # 读取并添加卡司信息
                index = i + 1
                for i, s_artist in enumerate(row[index:]):
                    for musical_cast in musical_cast_list:
                        if musical_cast.role == role_id_list[i] and musical_cast.artist.name == s_artist:
                            show.cast.add(musical_cast)
                            show_count = Show.objects.filter(cast__artist=musical_cast.artist_id,
                                                             time=show.time).distinct().count()
                            if show_count > 1:
                                Conflict.objects.get_or_create(artist=musical_cast.artist, time=show.time)
                            break
