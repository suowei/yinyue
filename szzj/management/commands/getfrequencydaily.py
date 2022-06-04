from django.core.management.base import BaseCommand
import datetime
from szzj.models import Album, AlbumDataDaily


class Command(BaseCommand):
    help = 'Get frequency everyday.'

    def handle(self, *args, **options):
        yesterday = datetime.datetime.now().date() + datetime.timedelta(days=-1)
        album_list = Album.objects.filter(is_free=False, release_date__lte=yesterday)
        for album in album_list:
            yesterday_data = AlbumDataDaily.objects.filter(album=album, date=yesterday)[0:1]
            if len(yesterday_data) > 0:
                album.frequency = yesterday_data[0].count
            else:
                album.frequency = 0
            album.save()
