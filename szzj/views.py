from django.shortcuts import render
from django.views import generic
from django.utils import timezone
from django.db.models import Count

from .models import Artist, Album, AlbumData, AlbumInfo, Concert, Site


def index(request):
    album_info_list = AlbumInfo.objects.select_related('artist').order_by('sale_time').only(
        'title', 'artist_id', 'artist__name', 'sale_time', 'info')
    now = timezone.now()
    date = now.date() + timezone.timedelta(days=-30)
    album_list = Album.objects.filter(release_date__gte=date).select_related('artist').order_by('-release_date').only(
        'title', 'artist_id', 'artist__name', 'release_date', 'price', 'album_only',
        'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id', 'qq_count', 'qq_song_count', 'qq_money',
        'kugou_count', 'kugou_song_count', 'kugou_money', 'kuwo_count', 'kuwo_song_count', 'kuwo_money',
        'wyy_count', 'wyy_song_count', 'wyy_money', 'count', 'money')
    top_album_list = Album.objects.order_by('-money_today').filter(money_today__gt=0).select_related('artist')[:20]
    new_concert_list = Concert.objects.filter(date__gte=now).select_related(
        'tour', 'tour__artist', 'site', 'site__city').order_by('-id')[:15]
    date = now + timezone.timedelta(days=7)
    concert_list = Concert.objects.filter(date__gte=now, date__lt=date).select_related(
        'tour', 'tour__artist', 'site', 'site__city').order_by('date')
    context = {'album_list': album_list, 'album_info_list': album_info_list, 'top_album_list': top_album_list,
               'new_concert_list': new_concert_list, 'concert_list': concert_list}
    return render(request, 'szzj/index.html', context)


def new_album_index(request):
    album_info_list = AlbumInfo.objects.select_related('artist').order_by('sale_time').only(
        'title', 'artist_id', 'artist__name', 'sale_time', 'info')
    date = timezone.now().date() + timezone.timedelta(days=-30)
    album_list = Album.objects.filter(release_date__gte=date).select_related('artist').order_by('-release_date').only(
        'title', 'artist_id', 'artist__name', 'release_date', 'price', 'album_only',
        'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id', 'qq_count', 'qq_song_count', 'qq_money',
        'kugou_count', 'kugou_song_count', 'kugou_money', 'kuwo_count', 'kuwo_song_count', 'kuwo_money',
        'wyy_count', 'wyy_song_count', 'wyy_money', 'count', 'money')
    context = {'album_list': album_list, 'album_info_list': album_info_list}
    return render(request, 'szzj/new_album_list.html', context)


class TodayAlbumIndexView(generic.ListView):
    template_name = 'szzj/today_album_list.html'

    def get_queryset(self):
        return Album.objects.order_by('-money_today').filter(money_today__gt=0).select_related('artist')[:20]


class AlbumIndexView(generic.ListView):
    def get_queryset(self):
        return Album.objects.select_related('artist').order_by('-money').only('title', 'artist_id', 'artist__name',
                                                                              'release_date', 'price', 'album_only',
                                                                              'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id',
                                                                              'qq_count', 'qq_song_count', 'qq_money',
                                                                              'kugou_count', 'kugou_song_count', 'kugou_money',
                                                                              'kuwo_count', 'kuwo_song_count', 'kuwo_money',
                                                                              'wyy_count', 'wyy_song_count', 'wyy_money', 'money')


def album_sales_index(request):
    album_list = Album.objects.select_related('artist').order_by('-count').only(
        'title', 'artist_id', 'artist__name', 'release_date', 'is_album', 'price',
        'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id',
        'qq_count', 'kugou_count', 'kuwo_count', 'wyy_count', 'count')
    context = {'album_list': album_list}
    return render(request, 'szzj/album_sales_list.html', context)


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


def album_sales_year_index(request, year):
    album_list = Album.objects.filter(release_date__year=year).select_related('artist').order_by('-count').only(
        'title', 'artist_id', 'artist__name', 'release_date', 'is_album', 'price',
        'qq_id', 'kugou_id', 'kuwo_id', 'wyy_id',
        'qq_count', 'kugou_count', 'kuwo_count', 'wyy_count', 'count')
    context = {'album_list': album_list, 'year': year}
    return render(request, 'szzj/album_sales_list.html', context)


class ArtistDetailView(generic.DetailView):
    model = Artist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['album_list'] = Album.objects.filter(artist=self.kwargs['pk']).order_by('-release_date')
        now = timezone.now()
        context['concert_list_coming'] = Concert.objects.filter(
            tour__artist=self.kwargs['pk'], date__gte=now).order_by('date').select_related('tour', 'site', 'site__city')
        context['concert_list_done'] = Concert.objects.filter(
            tour__artist=self.kwargs['pk'], date__lt=now).order_by('-date').select_related('tour', 'site', 'site__city')
        return context


def artist_index(request):
    album_list = Album.objects.order_by('-artist__money', 'release_date').select_related('artist').only('title', 'artist', 'release_date', 'money')
    for i in range(0, len(album_list)):
        if i == 0 or album_list[i].artist_id != album_list[i-1].artist_id:
            album_list[i].first = True
    context = {'album_list': album_list}
    return render(request, 'szzj/artist_list.html', context)


class AlbumDetailView(generic.DetailView):
    model = Album

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_list'] = AlbumData.objects.filter(album=self.kwargs['pk']).order_by('-id')[:144]
        return context


class ConcertIndexView(generic.ListView):
    def get_queryset(self):
        return Concert.objects.select_related('tour', 'tour__artist', 'site', 'site__city').filter(
            date__gte=timezone.now()).order_by('date').only('tour__artist__name', 'tour__title', 'date',
                                                            'site__city__name', 'site__name')


def concert_year_index(request, year):
    now = timezone.now()
    if year == now.year:
        artist_list = Artist.objects.filter(tour__concert__date__year=year, tour__concert__date__lte=now).annotate(
            num_concert=Count('tour__concert')).only('name').order_by('-num_concert')
        concert_list = Concert.objects.select_related('tour', 'site', 'site__city').filter(
            date__year=year, date__lte=now).order_by('date').only('tour__artist_id', 'tour__title', 'date',
                                                                  'site__city__name', 'site__name')
    else:
        artist_list = Artist.objects.filter(tour__concert__date__year=year).annotate(
            num_concert=Count('tour__concert')).only('name').order_by('-num_concert')
        concert_list = Concert.objects.select_related('tour', 'site', 'site__city').filter(
            date__year=year).order_by('date').only('tour__artist_id', 'tour__title', 'date',
                                                   'site__city__name', 'site__name')
    for artist in artist_list:
        artist.concert_list = []
        for concert in concert_list:
            if concert.tour.artist_id == artist.id:
                artist.concert_list.append(concert)
    context = {'year': year, 'artist_list': artist_list}
    return render(request, 'szzj/concert_year_list.html', context)


class SiteIndexView(generic.ListView):
    def get_queryset(self):
        return Site.objects.select_related('city').order_by('city', '-seats')


class SiteDetailView(generic.DetailView):
    model = Site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['concert_list_coming'] = Concert.objects.filter(
            site=self.kwargs['pk'], date__gte=now).order_by('date').select_related('tour', 'tour__artist')
        context['concert_list_done'] = Concert.objects.filter(
            site=self.kwargs['pk'], date__lt=now).order_by('-date').select_related('tour', 'tour__artist')
        return context
