from django.core.management.base import BaseCommand
from django.utils import timezone
from szzj.models import Album, AlbumData


class Command(BaseCommand):
    help = 'Get sale data today.'

    def handle(self, *args, **options):
        album_list = Album.objects.all()
        now = timezone.now()
        zero_today = now - timezone.timedelta(hours=now.hour + 8, minutes=now.minute, seconds=now.second,
                                              microseconds=now.microsecond)
        for album in album_list:
            initial_data_today = AlbumData.objects.filter(time__gte=zero_today, album=album).order_by('id')[0:1]
            if len(initial_data_today) > 0:
                album.qq_count_today = album.qq_count - initial_data_today[0].qq_count
                album.qq_song_count_today = album.qq_song_count - initial_data_today[0].qq_song_count
                album.qq_money_today = album.qq_money - initial_data_today[0].qq_money
                album.kugou_count_today = album.kugou_count - initial_data_today[0].kugou_count
                album.kugou_song_count_today = album.kugou_song_count - initial_data_today[0].kugou_song_count
                album.kugou_money_today = album.kugou_money - initial_data_today[0].kugou_money
                album.kuwo_count_today = album.kuwo_count - initial_data_today[0].kuwo_count
                album.kuwo_song_count_today = album.kuwo_song_count - initial_data_today[0].kuwo_song_count
                album.kuwo_money_today = album.kuwo_money - initial_data_today[0].kuwo_money
                album.wyy_count_today = album.wyy_count - initial_data_today[0].wyy_count
                album.wyy_money_today = album.wyy_money - initial_data_today[0].wyy_money
                album.count_today = album.count - initial_data_today[0].count
                album.money_today = album.money - initial_data_today[0].money
            else:
                album.qq_count_today = 0
                album.qq_song_count_today = 0
                album.qq_money_today = 0
                album.kugou_count_today = 0
                album.kugou_song_count_today = 0
                album.kugou_money_today = 0
                album.kuwo_count_today = 0
                album.kuwo_song_count_today = 0
                album.kuwo_money_today = 0
                album.wyy_count_today = 0
                album.wyy_money_today = 0
                album.count_today = 0
                album.money_today = 0
            album.save()
