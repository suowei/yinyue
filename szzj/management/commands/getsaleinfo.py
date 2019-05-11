from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone
from urllib import request, parse
import json
from decimal import Decimal
from szzj.models import Artist, Album, AlbumData


class Command(BaseCommand):
    help = 'Get sale data.'

    def handle(self, *args, **options):
        album_list = Album.objects.all()
        for album in album_list:
            if album.qq_id:
                url = 'https://c.y.qq.com/v8/fcg-bin/musicmall.fcg?cmd=get_album_buy_page&albumid=' + album.qq_id.__str__()
                with request.urlopen(url) as f:
                    data = f.read().decode('gbk')
                    json_data = json.loads(data[18:-1])
                    info = json_data['data']['sale_info']
                    album.qq_count = info['album_count']
                    album.qq_song_count = info['total_song_count']
                    album.qq_money = Decimal(info['sale_money'])

            if album.kugou_id:
                if album.kugou_id > 69486 and album.kugou_id != 90201:
                    url = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getBuyNum?topic_id=' + album.kugou_id.__str__()
                else:
                    url = 'http://zhuanji.kugou.com/index.php?r=commonchargeV2/getBuyNum&topic_id=' + album.kugou_id.__str__()
                with request.urlopen(url) as f:
                    data = f.read().decode('utf-8')
                    json_data = json.loads(data)
                    album.kugou_count = json_data['buy_num']
                    album.kugou_money = album.price * album.kugou_count
                if album.kugou_album_id:
                    url = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getSongsInfo?album_id=' + album.kugou_album_id.__str__() + '&hashs=' + album.kugou_hashs
                    with request.urlopen(url) as f:
                        data = f.read().decode('utf-8')
                        json_data = json.loads(data)
                        song_sales = json_data['data']
                        album.kugou_song_count = 0
                        actual_song_num = 0
                        for song_sale in song_sales:
                            if song_sale['pay_type'] > 0:
                                album.kugou_song_count += song_sale['buy_count']
                                actual_song_num += 1
                        album.kugou_money += (album.kugou_song_count - album.kugou_count * actual_song_num) * album.song_price

            if album.kuwo_id:
                data = {'key': album.kuwo_id, 'op': 'gfc'}
                req = request.Request('http://vip1.kuwo.cn/fans/admin/sysInfo',
                                      data=parse.urlencode(data).encode('utf-8'))
                with request.urlopen(req) as f:
                    response = f.read().decode('utf-8')
                    json_data = json.loads(response)
                    docs = json_data['fans']['docs']
                    album.kuwo_count = int(docs['total_cnt'])
                    album.kuwo_song_count = int(docs['song_total_cnt'])
                    album.kuwo_money = album.price * album.kuwo_count
                    if not album.album_only and album.kuwo_song_count > 0:
                        album.kuwo_money += (album.kuwo_song_count - album.kuwo_count * album.song_num) * album.song_price

            if album.wyy_id:
                if not album.wyy_params:
                    req = request.Request('https://music.163.com/store/api/product/detail?id=' + album.wyy_id.__str__())
                    req.add_header('Referer', 'https://music.163.com/store/product/detail?id=' + album.wyy_id.__str__())
                    with request.urlopen(req) as f:
                        response = f.read().decode('utf-8')
                        json_data = json.loads(response)
                        album.wyy_count = json_data['sales']
                        album.wyy_money = album.price * album.wyy_count
                else:
                    data = {'params': album.wyy_params, 'encSecKey': album.wyy_encSecKey}
                    req = request.Request('https://music.163.com/weapi/vipmall/albumproduct/detail',
                                          data=parse.urlencode(data).encode('utf-8'))
                    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.116')
                    req.add_header('Cookie', '_iuqxldmzr_=32; _ntes_nnid=6f5d1bca43ec729e8282602fb832fda6,1544339887101; _ntes_nuid=6f5d1bca43ec729e8282602fb832fda6; __utmz=94650624.1544339888.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); WM_TID=fOqk5KJk8dRAQBFBEBd8b9dXsnCTxHUE; JSESSIONID-WYYY=f1bPtYWmY56lpA4QwvyQSe%2FjiCQkvM0Betc%2FHOkxZzfiDnlKjeKglOXmvTXQ7AbBV9PzSsbm%2BziUVlJhjeP7xKR0wmt5Po9rqsS5Ed8di0c2TWpPgwxRwfxpO2Vn%2F3qi9738C1GxtNZgZSCsuFdSu9bzr4sMhwJ3Y3aM6%5CX7725iF7YN%3A1544530566006; __utma=94650624.1924053452.1544339888.1544439650.1544528767.3; __utmc=94650624; WM_NI=hHAptLBX1Prj7Rff4OKPwlgZplx0SmlkRc9%2F5TtejVhC3BqECF%2Bj%2Fam6UdijxEdcvjgEdntU15w2VB%2FmFG73jEElfaqsAmlaUh3pe%2BxjFhg31D3dfP8BD90AvHKkiZ6cRmY%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8ff25289abb9d3bc4b92ef8ba7c55b828b8f84f36af794b7b7e939a1b9acb7f82af0fea7c3b92aac988f91f7488288ffb1f162f58eaa87b7458990b98de652b4b4b8d1d267b0b59e84bc25f78cbc86e95eac9dfda3f44f819ae58bae6bafea9b85ec62bc9bac84f562a59bac8ff75ff3ebb9d3d54aedb38aa8b639aa9b8b8de56bb3ad8f8eef6b97b8fd91e821bcb68a89e639f39cfd85e55cfc9e8cdab34bb698858cec52f6bd9e8edc37e2a3; __utmb=94650624.4.10.1544528767')
                    with request.urlopen(req) as f:
                        response = f.read().decode('utf-8')
                        json_data = json.loads(response)
                        info = json_data['product']
                        album.wyy_count = info['saleNum']
                        album.wyy_song_count = info['songSales']
                        album.wyy_money = album.price * album.wyy_count

            album.count = album.qq_count + album.kugou_count + album.kuwo_count + album.wyy_count
            money = album.qq_money + album.kugou_money + album.kuwo_money + album.wyy_money
            if album.money != money:
                album.money = money
                album.save()
                AlbumData.objects.create(
                    album=album, time=timezone.now(),
                    qq_count=album.qq_count, qq_song_count=album.qq_song_count, qq_money=album.qq_money,
                    kugou_count=album.kugou_count, kugou_song_count=album.kugou_song_count, kugou_money=album.kugou_money,
                    kuwo_count=album.kuwo_count, kuwo_song_count=album.kuwo_song_count, kuwo_money=album.kuwo_money,
                    wyy_count=album.wyy_count, wyy_song_count=album.wyy_song_count, wyy_money=album.wyy_money,
                    count=album.count, money=album.money)

        artist_list = Artist.objects.annotate(album_sum=Sum('album__money'))
        for artist in artist_list:
            if artist.album_sum:
                artist.money = artist.album_sum
                artist.save()
