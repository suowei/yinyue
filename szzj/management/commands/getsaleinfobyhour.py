from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone
from django.core.cache import cache
from django.core.paginator import Paginator
from urllib import request, parse
import json
import datetime
from decimal import Decimal
from szzj.models import Artist, Album, AlbumData, AlbumDataDaily


class Command(BaseCommand):
    help = 'Get sale data.'

    qq_url = 'https://c.y.qq.com/v8/fcg-bin/musicmall.fcg?cmd=get_album_buy_page&albumid='
    kugou_url = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getBuyNum?topic_id='
    kugou_url_old = 'http://zhuanji.kugou.com/index.php?r=commonchargeV2/getBuyNum&topic_id='
    kugou_url_song = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getSongsInfo?album_id='
    kuwo_url = 'https://vip1.kuwo.cn/fans/admin/sysInfo'
    wyy_url_new = 'https://interface.music.163.com/api/vipmall/albumproduct/sales/v2?albumId='
    wyy_url_album = 'https://interface.music.163.com/api/vipmall/albumproduct/album/query/sales?albumIds='
    wyy_url = 'https://music.163.com/weapi/batch'
    wyy_url_ref = 'https://music.163.com/octave/m/album/detail?id='
    wyy_url_old = 'https://music.163.com/store/api/product/detail?id='
    wyy_url_old_ref = 'https://music.163.com/store/product/detail?id='
    wyy_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.116'
    wyy_cookie = '_iuqxldmzr_=32; _ntes_nnid=6f5d1bca43ec729e8282602fb832fda6,1544339887101; _ntes_nuid=6f5d1bca43ec729e8282602fb832fda6; __utmz=94650624.1544339888.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); WM_TID=fOqk5KJk8dRAQBFBEBd8b9dXsnCTxHUE; JSESSIONID-WYYY=f1bPtYWmY56lpA4QwvyQSe%2FjiCQkvM0Betc%2FHOkxZzfiDnlKjeKglOXmvTXQ7AbBV9PzSsbm%2BziUVlJhjeP7xKR0wmt5Po9rqsS5Ed8di0c2TWpPgwxRwfxpO2Vn%2F3qi9738C1GxtNZgZSCsuFdSu9bzr4sMhwJ3Y3aM6%5CX7725iF7YN%3A1544530566006; __utma=94650624.1924053452.1544339888.1544439650.1544528767.3; __utmc=94650624; WM_NI=hHAptLBX1Prj7Rff4OKPwlgZplx0SmlkRc9%2F5TtejVhC3BqECF%2Bj%2Fam6UdijxEdcvjgEdntU15w2VB%2FmFG73jEElfaqsAmlaUh3pe%2BxjFhg31D3dfP8BD90AvHKkiZ6cRmY%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8ff25289abb9d3bc4b92ef8ba7c55b828b8f84f36af794b7b7e939a1b9acb7f82af0fea7c3b92aac988f91f7488288ffb1f162f58eaa87b7458990b98de652b4b4b8d1d267b0b59e84bc25f78cbc86e95eac9dfda3f44f819ae58bae6bafea9b85ec62bc9bac84f562a59bac8ff75ff3ebb9d3d54aedb38aa8b639aa9b8b8de56bb3ad8f8eef6b97b8fd91e821bcb68a89e639f39cfd85e55cfc9e8cdab34bb698858cec52f6bd9e8edc37e2a3; __utmb=94650624.4.10.1544528767'
    migu_url = 'https://c.musicapp.migu.cn/MIGUM3.0/strategy/album-sub-rank/v1.0?queryType=06&resourceId='
    migu_header = {'channel': '014X031'}

    def add_arguments(self, parser):
        parser.add_argument('hour', nargs='?', type=int)

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        today = now.date()
        if now.hour == 0 and now.minute < 30:
            today += datetime.timedelta(days=-1)
        start_time = datetime.datetime(today.year, today.month, today.day, 0, 29, 0)
        hour = options['hour']
        if hour == 0:
            album_list = Album.objects.filter(is_free=False, frequency__gte=48).order_by('-id')
        elif hour == 1:
            album_list = Album.objects.filter(is_free=False, frequency__range=(24, 47)).order_by('-id')
        elif hour == 2:
            album_list = Album.objects.filter(is_free=False, frequency__range=(12, 23)).order_by('-id')
        elif hour == 4:
            album_list = Album.objects.filter(is_free=False, frequency__range=(6, 11)).order_by('-id')
        elif hour == 8:
            album_list = Album.objects.filter(is_free=False, frequency__range=(3, 5)).order_by('-id')
        elif hour == 12:
            album_list = Album.objects.filter(is_free=False, frequency__range=(1, 2)).order_by('-id')
        elif hour == 24:
            album_list = Album.objects.filter(is_free=False, frequency=0).order_by('-id')
        else:
            album_list = Album.objects.filter(is_free=False).order_by('-id')
        for album in album_list:
            if album.qq_id:
                url = self.qq_url + str(album.qq_id)
                for qq_i in range(10):
                    with request.urlopen(url) as f:
                        data = f.read().decode('gbk')
                        json_data = json.loads(data[18:-1])
                        if 'data' in json_data.keys():
                            info = json_data['data']['sale_info']
                            album.qq_count = info['album_count']
                            album.qq_song_count = info['total_song_count']
                            album.qq_money = Decimal(info['sale_money'])
                            break

            if album.kugou_id:
                if album.kugou_id > 69486 and album.kugou_id != 90201:
                    url = self.kugou_url + str(album.kugou_id)
                else:
                    url = self.kugou_url_old + str(album.kugou_id)
                with request.urlopen(url) as f:
                    data = f.read().decode('utf-8')
                    json_data = json.loads(data)
                    album.kugou_count = json_data['buy_num']
                    album.kugou_money = album.price * album.kugou_count
                    album.kugou_song_count = 0
                if album.kugou_album_id:
                    url = self.kugou_url_song + str(album.kugou_album_id)
                    with request.urlopen(url) as f:
                        data = f.read().decode('utf-8')
                        json_data = json.loads(data)
                        data = json_data['data'][0]
                        album.kugou_count = data['buy_count']
                        buy_count_audios = data['buy_count_audios']
                        album.kugou_song_count = album.kugou_count * album.song_num + buy_count_audios
                        album.kugou_money = album.price * album.kugou_count + buy_count_audios * album.song_price

            if album.kuwo_id:
                data = {'key': album.kuwo_id, 'op': 'gfc'}
                req = request.Request(self.kuwo_url, data=parse.urlencode(data).encode('utf-8'))
                with request.urlopen(req) as f:
                    response = f.read().decode('utf-8')
                    json_data = json.loads(response)
                    docs = json_data['fans']['docs']
                    album.kuwo_count = int(docs['total_cnt'])
                    album.kuwo_song_count = int(docs['song_total_cnt'])
                    album.kuwo_money = album.price * album.kuwo_count
                    if not album.album_only and album.kuwo_song_count > 0:
                        album.kuwo_money += (album.kuwo_song_count - album.kuwo_count * album.song_num) * album.song_price

            if album.wyy_id and album.id != 41:
                req = request.Request(self.wyy_url_new + str(album.wyy_id))
                for wyy_i in range(10):
                    with request.urlopen(req) as f:
                        response = f.read().decode('utf-8')
                        json_data = json.loads(response)
                        if json_data['code'] == 200:
                            if json_data['data']['salesDisplayType'] == 0:
                                album.wyy_count = json_data['data']['sales']
                                album.wyy_song_count = 0
                                album.wyy_money = album.price * album.wyy_count
                            else:
                                album.wyy_song_count = json_data['data']['sales']
                                req = request.Request(self.wyy_url_album + str(album.wyy_id))
                                with request.urlopen(req) as f2:
                                    response = f2.read().decode('utf-8')
                                    json_data = json.loads(response)
                                    album.wyy_count = json_data['data'][str(album.wyy_id)]
                                    album.wyy_money = album.price * album.wyy_count
                                    if not album.album_only and album.wyy_song_count > 0:
                                        album.wyy_money += (album.wyy_song_count - album.wyy_count * album.song_num) * album.song_price
                            break

            if album.migu_id:
                url = self.migu_url + str(album.migu_id)
                req = request.Request(url, headers=self.migu_header)
                for migu_i in range(10):
                    with request.urlopen(req) as f:
                        response = f.read().decode('utf-8')
                        json_data = json.loads(response)
                        if json_data['code'] == '000000':
                            if json_data['subDAlbumCounts']:
                                album.migu_count = int(json_data['subDAlbumCounts'][0]['sum'])
                                album.migu_money = album.price * album.migu_count
                            break

            album.count = album.qq_count + album.kugou_count + album.kuwo_count + album.wyy_count + album.migu_count
            money = album.qq_money + album.kugou_money + album.kuwo_money + album.wyy_money + album.migu_money
            if album.money != money:
                album.money = money
                album.save()
                AlbumData.objects.create(
                    album=album, time=timezone.now(),
                    qq_count=album.qq_count, qq_song_count=album.qq_song_count, qq_money=album.qq_money,
                    kugou_count=album.kugou_count, kugou_song_count=album.kugou_song_count, kugou_money=album.kugou_money,
                    kuwo_count=album.kuwo_count, kuwo_song_count=album.kuwo_song_count, kuwo_money=album.kuwo_money,
                    wyy_count=album.wyy_count, wyy_song_count=album.wyy_song_count, wyy_money=album.wyy_money,
                    migu_count=album.migu_count, migu_money=album.migu_money,
                    count=album.count, money=album.money)

                initial_data = AlbumData.objects.filter(album=album, time__lte=start_time).order_by('-id')[0:1]
                if len(initial_data) == 0:
                    initial_data = AlbumData.objects.filter(album=album).order_by('id')[0:1]
                initial_data = initial_data[0]
                qq_count_today = album.qq_count - initial_data.qq_count
                qq_song_count_today = album.qq_song_count - initial_data.qq_song_count
                qq_money_today = album.qq_money - initial_data.qq_money
                kugou_count_today = album.kugou_count - initial_data.kugou_count
                kugou_song_count_today = album.kugou_song_count - initial_data.kugou_song_count
                kugou_money_today = album.kugou_money - initial_data.kugou_money
                kuwo_count_today = album.kuwo_count - initial_data.kuwo_count
                kuwo_song_count_today = album.kuwo_song_count - initial_data.kuwo_song_count
                kuwo_money_today = album.kuwo_money - initial_data.kuwo_money
                wyy_count_today = album.wyy_count - initial_data.wyy_count
                wyy_song_count_today = album.wyy_song_count - initial_data.wyy_song_count
                wyy_money_today = album.wyy_money - initial_data.wyy_money
                migu_count_today = album.migu_count - initial_data.migu_count
                migu_money_today = album.migu_money - initial_data.migu_money
                count_today = album.count - initial_data.count
                money_today = album.money - initial_data.money
                sale_today = AlbumDataDaily.objects.filter(album=album, date=today)[0:1]
                if len(sale_today) > 0:
                    sale_today = sale_today[0]
                    sale_today.qq_count = qq_count_today
                    sale_today.qq_song_count = qq_song_count_today
                    sale_today.qq_money = qq_money_today
                    sale_today.kugou_count = kugou_count_today
                    sale_today.kugou_song_count = kugou_song_count_today
                    sale_today.kugou_money = kugou_money_today
                    sale_today.kuwo_count = kuwo_count_today
                    sale_today.kuwo_song_count = kuwo_song_count_today
                    sale_today.kuwo_money = kuwo_money_today
                    sale_today.wyy_count = wyy_count_today
                    sale_today.wyy_song_count = wyy_song_count_today
                    sale_today.wyy_money = wyy_money_today
                    sale_today.migu_count = migu_count_today
                    sale_today.migu_money = migu_money_today
                    sale_today.count = count_today
                    sale_today.money = money_today
                    sale_today.save()
                else:
                    AlbumDataDaily.objects.create(
                        album=album, date=today,
                        qq_count=qq_count_today, qq_song_count=qq_song_count_today, qq_money=qq_money_today,
                        kugou_count=kugou_count_today, kugou_song_count=kugou_song_count_today,
                        kugou_money=kugou_money_today,
                        kuwo_count=kuwo_count_today, kuwo_song_count=kuwo_song_count_today,
                        kuwo_money=kuwo_money_today,
                        wyy_count=wyy_count_today, wyy_song_count=wyy_song_count_today, wyy_money=wyy_money_today,
                        migu_count=migu_count_today, migu_money=migu_money_today,
                        count=count_today, money=money_today)

        if hour != 0:
            return

        artist_list = Artist.objects.annotate(album_sum=Sum('album__money'))
        for artist in artist_list:
            if artist.album_sum:
                artist.money = artist.album_sum
                artist.save()

        cache.set('latest_time', now)

        album_list = Album.objects.select_related('artist').order_by('-money')
        paginator = Paginator(album_list, 100)
        top_albums = paginator.get_page(1)
        cache.set('top_albums', top_albums)

        artist_list = Artist.objects.filter(money__gt=0).order_by('-money').values_list('pk')
        paginator = Paginator(artist_list, 50)
        artists = paginator.get_page(1)
        albums = Album.objects.filter(artist__in=artists).order_by(
            '-artist__money', 'release_date').select_related('artist').only(
            'title', 'artist', 'release_date', 'money')
        for i in range(0, len(albums)):
            if i == 0 or albums[i].artist_id != albums[i - 1].artist_id:
                albums[i].first = True
        albums.page_range = artists.paginator.page_range
        albums.number = artists.number
        cache.set('top_artists', albums)

        top_albums_today = AlbumDataDaily.objects.filter(date=today).order_by('-money').select_related(
            'album', 'album__artist')[:20]
        cache.set('top_albums_today', top_albums_today)
