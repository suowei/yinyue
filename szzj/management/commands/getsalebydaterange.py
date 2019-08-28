from django.core.management.base import BaseCommand
import datetime
from szzj.models import Album, AlbumData, AlbumDataDaily


class Command(BaseCommand):
    help = 'Get sales in a date range.'

    def add_arguments(self, parser):
        parser.add_argument('start_year', type=int)
        parser.add_argument('start_month', type=int)
        parser.add_argument('start_day', type=int)
        parser.add_argument('end_year', type=int)
        parser.add_argument('end_month', type=int)
        parser.add_argument('end_day', type=int)

    def handle(self, *args, **options):
        date = datetime.date(options['start_year'], options['start_month'], options['start_day'])
        end_date = datetime.date(options['end_year'], options['end_month'], options['end_day'])
        album_list = Album.objects.all()
        while date <= end_date:
            start_time = datetime.datetime(date.year, date.month, date.day, 0, 20, 0)
            end_time = start_time + datetime.timedelta(days=1)
            for album in album_list:
                initial_data = AlbumData.objects.filter(album=album, time__lte=start_time).order_by('-id')[0:1]
                if len(initial_data) == 0:
                    initial_data = AlbumData.objects.filter(album=album).order_by('id')[0:1]
                    if len(initial_data) == 0:
                        continue
                initial_data = initial_data[0]
                final_data = AlbumData.objects.filter(album=album, time__lte=end_time).order_by('-id')[0:1]
                if len(final_data) == 0:
                    continue
                final_data = final_data[0]
                if final_data.money != initial_data.money:
                    qq_count = final_data.qq_count - initial_data.qq_count
                    qq_song_count = final_data.qq_song_count - initial_data.qq_song_count
                    qq_money = final_data.qq_money - initial_data.qq_money
                    kugou_count = final_data.kugou_count - initial_data.kugou_count
                    kugou_song_count = final_data.kugou_song_count - initial_data.kugou_song_count
                    kugou_money = final_data.kugou_money - initial_data.kugou_money
                    kuwo_count = final_data.kuwo_count - initial_data.kuwo_count
                    kuwo_song_count = final_data.kuwo_song_count - initial_data.kuwo_song_count
                    kuwo_money = final_data.kuwo_money - initial_data.kuwo_money
                    wyy_count = final_data.wyy_count - initial_data.wyy_count
                    wyy_song_count = final_data.wyy_song_count - initial_data.wyy_song_count
                    wyy_money = final_data.wyy_money - initial_data.wyy_money
                    count = final_data.count - initial_data.count
                    money = final_data.money - initial_data.money
                    data = AlbumDataDaily.objects.filter(album=album, date=date)[0:1]
                    if len(data) > 0:
                        data = data[0]
                        data.qq_count = qq_count
                        data.qq_song_count = qq_song_count
                        data.qq_money = qq_money
                        data.kugou_count = kugou_count
                        data.kugou_song_count = kugou_song_count
                        data.kugou_money = kugou_money
                        data.kuwo_count = kuwo_count
                        data.kuwo_song_count = kuwo_song_count
                        data.kuwo_money = kuwo_money
                        data.wyy_count = wyy_count
                        data.wyy_song_count = wyy_song_count
                        data.wyy_money = wyy_money
                        data.count = count
                        data.money = money
                        data.save()
                    else:
                        AlbumDataDaily.objects.create(
                            album=album, date=date,
                            qq_count=qq_count, qq_song_count=qq_song_count, qq_money=qq_money,
                            kugou_count=kugou_count, kugou_song_count=kugou_song_count, kugou_money=kugou_money,
                            kuwo_count=kuwo_count, kuwo_song_count=kuwo_song_count, kuwo_money=kuwo_money,
                            wyy_count=wyy_count, wyy_song_count=wyy_song_count, wyy_money=wyy_money,
                            count=count, money=money)
            date += datetime.timedelta(days=1)
