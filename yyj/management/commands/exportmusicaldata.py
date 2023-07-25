from django.core.management.base import BaseCommand
import csv
import datetime
from django.utils import timezone
from yyj.models import Musical, MusicalStaff, MusicalProduces


class Command(BaseCommand):

    def handle(self, *args, **options):
        musical_list_zz = Musical.objects.filter(progress=Musical.SETUP).order_by('premiere_date')
        musical_list_dd = Musical.objects.filter(progress=Musical.PROMOTE).order_by('premiere_date')
        musical_list_ss = Musical.objects.filter(progress=Musical.PRESENT).order_by('-premiere_date')
        count = musical_list_zz.count() + musical_list_dd.count() + musical_list_ss.count()
        filename = 'download/musical.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['音乐剧', '原创性', '进度', '首演日期', '其他信息', '制作公司', '主创信息'])
            for musical in musical_list_zz:
                if musical.is_original:
                    original_string = '原创'
                else:
                    original_string = '引进'
                if musical.premiere_date_text:
                    date_string = musical.premiere_date_text
                else:
                    date_string = musical.premiere_date
                previous = None
                produce_string = ''
                produce_list = MusicalProduces.objects.filter(musical=musical).select_related('produce').order_by('seq')
                for produce in produce_list:
                    if previous and previous.title == produce.title:
                        produce_string += ' ' + produce.produce.name
                    elif previous:
                        produce_string += '\n' + produce.title + '：' + produce.produce.name
                    else:
                        produce_string += produce.title + '：' + produce.produce.name
                    previous = produce
                previous = None
                staff_string = ''
                staff_list = MusicalStaff.objects.filter(musical=musical).select_related('artist').order_by('seq')
                for staff in staff_list:
                    if previous and previous.job == staff.job:
                        staff_string += ' ' + staff.artist.name
                    elif previous:
                        staff_string += '\n' + staff.job + '：' + staff.artist.name
                    else:
                        staff_string += staff.job + '：' + staff.artist.name
                    previous = staff
                writer.writerow([
                    musical.name,
                    original_string,
                    '制作',
                    date_string,
                    musical.info,
                    produce_string,
                    staff_string,
                ])
            for musical in musical_list_dd:
                if musical.is_original:
                    original_string = '原创'
                else:
                    original_string = '引进'
                if musical.premiere_date_text:
                    date_string = musical.premiere_date_text
                else:
                    date_string = musical.premiere_date
                previous = None
                produce_string = ''
                produce_list = MusicalProduces.objects.filter(musical=musical).select_related('produce').order_by('seq')
                for produce in produce_list:
                    if previous and previous.title == produce.title:
                        produce_string += ' ' + produce.produce.name
                    elif previous:
                        produce_string += '\n' + produce.title + '：' + produce.produce.name
                    else:
                        produce_string += produce.title + '：' + produce.produce.name
                    previous = produce
                previous = None
                staff_string = ''
                staff_list = MusicalStaff.objects.filter(musical=musical).select_related('artist').order_by('seq')
                for staff in staff_list:
                    if previous and previous.job == staff.job:
                        staff_string += ' ' + staff.artist.name
                    else:
                        staff_string += '\n' + staff.job + '：' + staff.artist.name
                    previous = staff
                writer.writerow([
                    musical.name,
                    original_string,
                    '定档',
                    date_string,
                    musical.info,
                    produce_string,
                    staff_string,
                ])
            for musical in musical_list_ss:
                if musical.is_original:
                    original_string = '原创'
                else:
                    original_string = '引进'
                if musical.premiere_date_text:
                    date_string = musical.premiere_date_text
                else:
                    date_string = musical.premiere_date
                previous = None
                produce_string = ''
                produce_list = MusicalProduces.objects.filter(musical=musical).select_related('produce').order_by('seq')
                for produce in produce_list:
                    if previous and previous.title == produce.title:
                        produce_string += ' ' + produce.produce.name
                    else:
                        produce_string += '\n' + produce.title + '：' + produce.produce.name
                    previous = produce
                previous = None
                staff_string = ''
                staff_list = MusicalStaff.objects.filter(musical=musical).select_related('artist').order_by('seq')
                for staff in staff_list:
                    if previous and previous.job == staff.job:
                        staff_string += ' ' + staff.artist.name
                    elif previous:
                        staff_string += '\n' + staff.job + '：' + staff.artist.name
                    else:
                        staff_string += staff.job + '：' + staff.artist.name
                    previous = staff
                writer.writerow([
                    musical.name,
                    original_string,
                    '上演',
                    date_string,
                    musical.info,
                    produce_string,
                    staff_string,
                ])
        print(count)
