from django.shortcuts import render
from django.views import generic

from .models import Artist, Album


def index(request):
    album_list = Album.objects.order_by('-money').only('title', 'artist_name', 'artist_id', 'release_date', 'price', 'album_only',
                                                       'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id',
                                                       'qq_count', 'qq_song_count', 'qq_money',
                                                       'kugou_count', 'kugou_song_count', 'kugou_money',
                                                       'kuwo_count', 'kuwo_song_count', 'kuwo_money',
                                                       'wyy_count', 'wyy_song_count', 'wyy_money', 'money')
    context = {'album_list': album_list}
    return render(request, 'index.html', context)


class ArtistDetailView(generic.DetailView):
    model = Artist


def artist_index(request):
    album_list = Album.objects.order_by('-artist__money', 'release_date').select_related('artist').only('title', 'artist', 'release_date', 'money')
    for i in range(0, len(album_list)):
        if i == 0 or album_list[i].artist_id != album_list[i-1].artist_id:
            album_list[i].first = True
    context = {'album_list': album_list}
    return render(request, 'szzj/artist_index.html', context)
