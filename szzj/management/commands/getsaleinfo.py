from django.core.management.base import BaseCommand
from szzj.models import Album


class Command(BaseCommand):
    help = 'Get sale data.'

    def handle(self, *args, **options):
        i = Album.objects.count()
        while i > 0:
            album = Album.objects.get(id=i)
            album.get_sale_info()
            album.save()
            i -= 1

