from django.core.management.base import BaseCommand
from szzj.models import Album, AlbumDataDaily


class Command(BaseCommand):
    help = 'Get initial frequency.'

    def handle(self, *args, **options):
        album_list = Album.objects.all()
        for album in album_list:
            if album.is_free:
                album.frequency = 0
            else:
                recent_daily_data = AlbumDataDaily.objects.filter(album=album).order_by('-date')[0:1]
                if len(recent_daily_data) > 0:
                    album.frequency = recent_daily_data[0].count
                else:
                    album.frequency = 48
            album.save()
