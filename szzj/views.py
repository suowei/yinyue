from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count

from .models import Artist, Album, Concert, Site


def index(request):
    return HttpResponse("查看数字专辑销售数据请访问http://y.saoju.net/szzj/")


class AlbumIndexView(generic.ListView):
    def get_queryset(self):
        return Album.objects.select_related('artist').order_by('-money').only('title', 'artist_id', 'artist__name',
                                                                              'release_date', 'price', 'album_only',
                                                                              'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id',
                                                                              'qq_count', 'qq_song_count', 'qq_money',
                                                                              'kugou_count', 'kugou_song_count', 'kugou_money',
                                                                              'kuwo_count', 'kuwo_song_count', 'kuwo_money',
                                                                              'wyy_count', 'wyy_song_count', 'wyy_money', 'money')


def album_year_index(request, year):
    album_list = Album.objects.filter(release_date__year=year).select_related('artist').order_by('-money').only('title', 'artist_id', 'artist__name',
                                                                              'release_date', 'price', 'album_only',
                                                                              'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id',
                                                                              'qq_count', 'qq_song_count', 'qq_money',
                                                                              'kugou_count', 'kugou_song_count', 'kugou_money',
                                                                              'kuwo_count', 'kuwo_song_count', 'kuwo_money',
                                                                              'wyy_count', 'wyy_song_count', 'wyy_money', 'money')
    context = {'year': year, 'album_list': album_list}
    return render(request, 'szzj/album_list.html', context)


class ArtistDetailView(generic.DetailView):
    model = Artist


def artist_index(request):
    album_list = Album.objects.order_by('-artist__money', 'release_date').select_related('artist').only('title', 'artist', 'release_date', 'money')
    for i in range(0, len(album_list)):
        if i == 0 or album_list[i].artist_id != album_list[i-1].artist_id:
            album_list[i].first = True
    context = {'album_list': album_list}
    return render(request, 'szzj/artist_list.html', context)


class ConcertIndexView(generic.ListView):
    def get_queryset(self):
        return Concert.objects.select_related('artist', 'site').filter(
            date__gte=timezone.now()).order_by('date').only('artist__name', 'title', 'date', 'site__name')


def concert_year_index(request, year):
    now = timezone.now()
    if year == now.year:
        artist_list = Artist.objects.filter(concert__date__year=year, concert__date__lte=now).annotate(
            num_concert=Count('concert')).only('name').order_by('-num_concert')
        concert_list = Concert.objects.select_related('site').filter(
            date__year=year, date__lte=now).order_by('date').only('artist_id', 'title', 'date', 'site__name')
    else:
        artist_list = Artist.objects.filter(concert__date__year=year).annotate(
            num_concert=Count('concert')).only('name').order_by('-num_concert')
        concert_list = Concert.objects.select_related('site').filter(
            date__year=year).order_by('date').only('artist_id', 'title', 'date', 'site__name')
    for artist in artist_list:
        artist.concert_list = []
        for concert in concert_list:
            if concert.artist_id == artist.id:
                artist.concert_list.append(concert)
    context = {'year': year, 'artist_list': artist_list}
    return render(request, 'szzj/concert_year_list.html', context)


class SiteIndexView(generic.ListView):
    def get_queryset(self):
        return Site.objects.order_by('-seats')
