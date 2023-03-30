from django.shortcuts import render
from django.views import generic
from django.db.models import Count, Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.cache import cache
import datetime
import csv
import codecs

from .models import Artist, Album, AlbumData, AlbumDataDaily, AlbumInfo, Concert, City, Site


def index(request):
    album_info_list = AlbumInfo.objects.select_related('artist').order_by('sale_time').only(
        'title', 'artist_id', 'artist__name', 'sale_time', 'info')
    now = datetime.datetime.now()
    date = now.date() + datetime.timedelta(days=-30)
    album_list = Album.objects.filter(release_date__gte=date).select_related('artist').order_by('-release_date')
    top_album_list = cache.get('top_albums_today')
    if not top_album_list:
        today = now.date()
        if now.hour == 0 and now.minute < 30:
            today += datetime.timedelta(days=-1)
        top_album_list = AlbumDataDaily.objects.filter(date=today).order_by('-money').select_related(
            'album', 'album__artist')[:20]
    new_concert_list = Concert.objects.filter(date__gte=now).select_related(
        'tour', 'tour__artist', 'site', 'site__city').order_by('-id')[:10]
    date = now + datetime.timedelta(days=7)
    concert_list = Concert.objects.filter(date__gte=now, date__lt=date).select_related(
        'tour', 'tour__artist', 'site', 'site__city').order_by('date')
    context = {'album_list': album_list, 'album_info_list': album_info_list, 'latest_time': cache.get('latest_time'),
               'top_album_list': top_album_list, 'new_concert_list': new_concert_list, 'concert_list': concert_list}
    return render(request, 'szzj/index.html', context)


def new_album_index(request):
    album_info_list = AlbumInfo.objects.select_related('artist').order_by('sale_time').only(
        'title', 'artist_id', 'artist__name', 'sale_time', 'info')
    date = datetime.date.today() + datetime.timedelta(days=-30)
    album_list = Album.objects.filter(release_date__gte=date).select_related('artist').order_by('-release_date')
    context = {'album_list': album_list, 'album_info_list': album_info_list}
    return render(request, 'szzj/new_album_list.html', context)


def today_album_index(request):
    top_albums_today = cache.get('top_albums_today')
    if not top_albums_today:
        now = datetime.datetime.now()
        today = now.date()
        if now.hour == 0 and now.minute < 30:
            today += datetime.timedelta(days=-1)
        top_albums_today = AlbumDataDaily.objects.filter(date=today).order_by('-money').select_related(
            'album', 'album__artist')[:20]
    context = {'data_list': top_albums_today, 'latest_time': cache.get('latest_time')}
    return render(request, 'szzj/today_album_list.html', context)


def album_index(request):
    page = request.GET.get('page')
    albums = cache.get('top_albums')
    if not page and albums:
        context = {'albums': albums, 'latest_time': cache.get('latest_time')}
    else:
        album_list = Album.objects.select_related('artist').order_by('-money')
        paginator = Paginator(album_list, 100)
        albums = paginator.get_page(page)
        context = {'albums': albums}
    return render(request, 'szzj/album_list.html', context)


def album_sales_index(request):
    album_list = Album.objects.filter(is_album=True).select_related('artist').order_by('-count')[:50]
    single_list = Album.objects.filter(is_album=False).select_related('artist').order_by('-count')[:50]
    context = {'album_list': album_list, 'single_list': single_list}
    return render(request, 'szzj/album_sales_list.html', context)


def album_year_index(request, year):
    if year == 2014:
        album_list = Album.objects.filter(id=150).select_related('artist')[:1]
    elif year == 2016:
        album_list = Album.objects.filter(
            Q(release_date__year=2016) | Q(id=46)).select_related('artist').order_by('-money')
    else:
        album_list = Album.objects.filter(release_date__year=year).select_related('artist').order_by('-money')
    context = {'year': year, 'albums': album_list}
    return render(request, 'szzj/album_list.html', context)


def album_sales_year_index(request, year):
    if year == 2014:
        album_list = Album.objects.filter(id=150).select_related('artist')[:1]
        single_list = None
    else:
        if year == 2016:
            album_list = Album.objects.filter(
                Q(release_date__year=2016) & Q(is_album=True) | Q(id=46)).select_related('artist').order_by('-count')
        else:
            album_list = Album.objects.filter(
                release_date__year=year, is_album=True).select_related('artist').order_by('-count')
        single_list = Album.objects.filter(release_date__year=year, is_album=False).select_related('artist').order_by('-count')[:50]
    context = {'album_list': album_list, 'single_list': single_list, 'year': year}
    return render(request, 'szzj/album_sales_list.html', context)


class ArtistDetailView(generic.DetailView):
    model = Artist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['album_list'] = Album.objects.filter(artist=self.kwargs['pk']).order_by('-release_date')
        now = datetime.datetime.now()
        context['concert_list_coming'] = Concert.objects.filter(
            tour__artist=self.kwargs['pk'], date__gte=now).order_by('date').select_related('tour', 'site', 'site__city')
        context['concert_list_done'] = Concert.objects.filter(
            tour__artist=self.kwargs['pk'], date__lt=now).order_by('-date').select_related('tour', 'site', 'site__city')
        return context


def artist_index(request):
    page = request.GET.get('page')
    albums = cache.get('top_artists')
    if not page and albums:
        context = {'album_list': albums, 'latest_time': cache.get('latest_time')}
    else:
        artist_list = Artist.objects.filter(money__gt=0).order_by('-money').values_list('pk')
        paginator = Paginator(artist_list, 50)
        artists = paginator.get_page(page)
        albums = Album.objects.filter(artist__in=artists).order_by(
            '-artist__money', 'release_date').select_related('artist').only(
            'title', 'artist', 'release_date', 'money')
        for i in range(0, len(albums)):
            if i == 0 or albums[i].artist_id != albums[i - 1].artist_id:
                albums[i].first = True
        albums.page_range = artists.paginator.page_range
        albums.number = artists.number
        context = {'album_list': albums}
    return render(request, 'szzj/artist_list.html', context)


def album_detail(request, pk):
    album = Album.objects.get(pk=pk)
    daily_data = AlbumDataDaily.objects.filter(album=album).order_by('-id')
    paginator = Paginator(daily_data, 30)
    page = request.GET.get('page')
    daily_list = paginator.get_page(page)
    context = {'album': album, 'daily_list': daily_list}
    return render(request, 'szzj/album_detail.html', context)


def album_data_daily(request, album):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="album_data_daily.csv"'
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(['日期', '当日销量（张）', '当日销量（元）', 'QQ音乐（张）', 'QQ音乐（元）', '网易云音乐（张）', '网易云音乐（元）',
                     '酷狗音乐（张）', '酷狗音乐（元）', '酷我音乐（张）', '酷我音乐（元）', '咪咕音乐（张）', '咪咕音乐（元）'])
    data_list = AlbumDataDaily.objects.filter(album=album)
    for data in data_list:
        writer.writerow([data.date.strftime('%Y-%m-%d'), data.count, data.money,
                         data.qq_count, data.qq_money, data.wyy_count, data.wyy_money,
                         data.kugou_count, data.kugou_money, data.kuwo_count, data.kuwo_money,
                         data.migu_count, data.migu_money])
    return response


def album_data_daily_detail(request, album, year, month, day):
    start_time = datetime.datetime(year, month, day, 0, 0)
    end_time = datetime.datetime(year, month, day, 23, 59)
    data_list = AlbumData.objects.filter(album=album, time__range=(start_time, end_time))
    context = {'data_list': data_list}
    return render(request, 'szzj/album_data_daily_detail.html', context)


def album_download(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="szzj_{}.csv"'.format(datetime.datetime.now())
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(['专辑', '歌手', '发行日期', '价格（元）', '歌曲数', '总销量（张）', '总销量（元）',
                     'QQ音乐（张）', 'QQ音乐（元）', '网易云音乐（张）', '网易云音乐（元）',
                     '酷狗音乐（张）', '酷狗音乐（元）', '酷我音乐（张）', '酷我音乐（元）', '咪咕音乐（张）', '咪咕音乐（元）'])
    album_list = Album.objects.select_related('artist').order_by('-money')
    for album in album_list:
        writer.writerow([album.title, album.artist.name, album.release_date, album.price, album.song_num,
                         album.count, album.money, album.qq_count, album.qq_money, album.wyy_count, album.wyy_money,
                         album.kugou_count, album.kugou_money, album.kuwo_count, album.kuwo_money,
                         album.migu_count, album.migu_money])
    return response


class ConcertIndexView(generic.ListView):
    def get_queryset(self):
        return Concert.objects.select_related('tour', 'tour__artist', 'site', 'site__city').filter(
            date__gte=datetime.datetime.now()).order_by('date')


def concert_year_index(request, year):
    now = datetime.datetime.now()
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


class CityDetailView(generic.DetailView):
    model = City

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.datetime.now()
        context['concert_list_coming'] = Concert.objects.filter(
            site__city=self.kwargs['pk'], date__gte=now).order_by('date').select_related('tour', 'tour__artist', 'site')
        context['concert_list_done'] = Concert.objects.filter(
            site__city=self.kwargs['pk'], date__lt=now).order_by('-date').select_related('tour', 'tour__artist', 'site')
        return context


class SiteIndexView(generic.ListView):
    def get_queryset(self):
        return Site.objects.select_related('city').order_by('city', '-seats')


class SiteDetailView(generic.DetailView):
    model = Site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.datetime.now()
        context['concert_list_coming'] = Concert.objects.filter(
            site=self.kwargs['pk'], date__gte=now).order_by('date').select_related('tour', 'tour__artist')
        context['concert_list_done'] = Concert.objects.filter(
            site=self.kwargs['pk'], date__lt=now).order_by('-date').select_related('tour', 'tour__artist')
        return context


def search(request):
    q = request.GET['q']
    artist_list = Artist.objects.filter(name__icontains=q)
    album_list = Album.objects.filter(title__icontains=q).select_related('artist')
    context = {'artist_list': artist_list, 'album_list': album_list}
    return render(request, 'szzj/search.html', context)
