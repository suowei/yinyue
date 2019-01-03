from django.core.management.base import BaseCommand
from django.db.models import Sum
from szzj.models import Artist, Album


class Command(BaseCommand):
    help = 'Get sale data.'

    def handle(self, *args, **options):
        album_list = Album.objects.only('song_num', 'price', 'album_only', 'song_price',
                                        'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id', 'wyy_params', 'wyy_encSecKey',
                                        'qq_count', 'qq_song_count', 'qq_money',
                                        'kugou_count', 'kugou_song_count', 'kugou_money',
                                        'kuwo_count', 'kuwo_song_count', 'kuwo_money',
                                        'wyy_count', 'wyy_song_count', 'wyy_money', 'migu_money', 'money')
        for album in album_list:
            album.get_sale_info()
            album.save()

        artist_list = Artist.objects.annotate(album_sum=Sum('album__money'))
        for artist in artist_list:
            if artist.album_sum:
                artist.money = artist.album_sum
                artist.save()
