from django.core.management.base import BaseCommand
from szzj.models import Album


class Command(BaseCommand):
    help = 'Get sale data.'

    def handle(self, *args, **options):
        album_list = Album.objects.all()
        for album in album_list:
            album.get_sale_info()
            album.save()

