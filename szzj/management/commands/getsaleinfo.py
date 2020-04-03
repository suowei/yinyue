from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone
from urllib import request, parse
import json
import datetime
from decimal import Decimal
from Crypto.Cipher import AES
import base64
import codecs
from szzj.models import Artist, Album, AlbumData, AlbumDataDaily


def to_16(key):
    while len(key) % 16 != 0:
        key += '\0'
    return str.encode(key)


def pad2(s):
    bs = AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def aes_encrypt(text, key, iv):
    encryptor = AES.new(to_16(key), AES.MODE_CBC, to_16(iv))
    encrypt_aes = encryptor.encrypt(str.encode(pad2(text)))
    encrypt_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
    return encrypt_text


def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pub_key, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


class Command(BaseCommand):
    help = 'Get sale data.'

    qq_url = 'https://c.y.qq.com/v8/fcg-bin/musicmall.fcg?cmd=get_album_buy_page&albumid='
    kugou_url = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getBuyNum?topic_id='
    kugou_url_old = 'http://zhuanji.kugou.com/index.php?r=commonchargeV2/getBuyNum&topic_id='
    kugou_url_song = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getSongsInfo?album_id='
    kuwo_url = 'https://vip1.kuwo.cn/fans/admin/sysInfo'
    wyy_url = 'https://music.163.com/weapi/batch'
    wyy_url_ref = 'https://music.163.com/octave/m/album/detail?id='
    wyy_url_old = 'https://music.163.com/store/api/product/detail?id='
    wyy_url_old_ref = 'https://music.163.com/store/product/detail?id='
    wyy_g = '0CoJUm6Qyw8W8jud'
    wyy_b = "010001"
    wyy_c = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    wyy_i = '0123456789abcdef'
    wyy_iv = "0102030405060708"
    wyy_api_sales = '/api/vipmall/albumproduct/album/query/sales'
    wyy_api_song_sales = '/api/vipmall/albumproduct/album/query/song/sales'
    wyy_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.116'
    wyy_cookie = '_iuqxldmzr_=32; _ntes_nnid=6f5d1bca43ec729e8282602fb832fda6,1544339887101; _ntes_nuid=6f5d1bca43ec729e8282602fb832fda6; __utmz=94650624.1544339888.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); WM_TID=fOqk5KJk8dRAQBFBEBd8b9dXsnCTxHUE; JSESSIONID-WYYY=f1bPtYWmY56lpA4QwvyQSe%2FjiCQkvM0Betc%2FHOkxZzfiDnlKjeKglOXmvTXQ7AbBV9PzSsbm%2BziUVlJhjeP7xKR0wmt5Po9rqsS5Ed8di0c2TWpPgwxRwfxpO2Vn%2F3qi9738C1GxtNZgZSCsuFdSu9bzr4sMhwJ3Y3aM6%5CX7725iF7YN%3A1544530566006; __utma=94650624.1924053452.1544339888.1544439650.1544528767.3; __utmc=94650624; WM_NI=hHAptLBX1Prj7Rff4OKPwlgZplx0SmlkRc9%2F5TtejVhC3BqECF%2Bj%2Fam6UdijxEdcvjgEdntU15w2VB%2FmFG73jEElfaqsAmlaUh3pe%2BxjFhg31D3dfP8BD90AvHKkiZ6cRmY%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8ff25289abb9d3bc4b92ef8ba7c55b828b8f84f36af794b7b7e939a1b9acb7f82af0fea7c3b92aac988f91f7488288ffb1f162f58eaa87b7458990b98de652b4b4b8d1d267b0b59e84bc25f78cbc86e95eac9dfda3f44f819ae58bae6bafea9b85ec62bc9bac84f562a59bac8ff75ff3ebb9d3d54aedb38aa8b639aa9b8b8de56bb3ad8f8eef6b97b8fd91e821bcb68a89e639f39cfd85e55cfc9e8cdab34bb698858cec52f6bd9e8edc37e2a3; __utmb=94650624.4.10.1544528767'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        today = now.date()
        if now.hour == 0 and now.minute < 30:
            today += datetime.timedelta(days=-1)
        start_time = datetime.datetime(today.year, today.month, today.day, 0, 20, 0)
        i = Album.objects.count()
        while i > 0:
            album = Album.objects.get(pk=i)
            i -= 1
            if album.qq_id:
                url = self.qq_url + str(album.qq_id)
                with request.urlopen(url) as f:
                    data = f.read().decode('gbk')
                    json_data = json.loads(data[18:-1])
                    info = json_data['data']['sale_info']
                    album.qq_count = info['album_count']
                    album.qq_song_count = info['total_song_count']
                    album.qq_money = Decimal(info['sale_money'])

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
                    album.kugou_song_count = album.kugou_count * album.song_num
                    url = self.kugou_url_song + str(album.kugou_album_id) + '&hashs=' + album.kugou_hashs
                    with request.urlopen(url) as f:
                        data = f.read().decode('utf-8')
                        json_data = json.loads(data)
                        song_sales = json_data['data']
                        for song_sale in song_sales:
                            extra_song_count = song_sale['buy_count'] - album.kugou_count
                            album.kugou_song_count += extra_song_count
                            if song_sale['pay_type'] > 0:
                                album.kugou_money += extra_song_count * album.song_price
                                continue
                            if song_sale['privilege'] == 0:
                                album.kugou_song_count -= album.kugou_count

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

            if album.wyy_id:
                if not album.wyy_params:
                    req = request.Request(self.wyy_url_old + str(album.wyy_id))
                    req.add_header('Referer', self.wyy_url_old_ref + str(album.wyy_id))
                    with request.urlopen(req) as f:
                        response = f.read().decode('utf-8')
                        json_data = json.loads(response)
                        album.wyy_count = json_data['sales']
                        album.wyy_money = album.price * album.wyy_count
                else:
                    wyy_enc_text = str({
                        self.wyy_api_sales: '{albumIds:' + str(album.wyy_id) + '}',
                        self.wyy_api_song_sales: '{albumId:' + str(album.wyy_id) + '}'
                    })
                    params = aes_encrypt(aes_encrypt(wyy_enc_text, self.wyy_g, self.wyy_iv), self.wyy_i, self.wyy_iv)
                    enc_sec_key = rsa_encrypt(self.wyy_i, self.wyy_b, self.wyy_c)
                    data = {'params': params, 'encSecKey': enc_sec_key}
                    req = request.Request(self.wyy_url, data=parse.urlencode(data).encode('utf-8'))
                    req.add_header('Referer', self.wyy_url_ref + str(album.wyy_id))
                    req.add_header('User-Agent', self.wyy_agent)
                    req.add_header('Cookie', self.wyy_cookie)
                    with request.urlopen(req) as f:
                        response = f.read().decode('utf-8')
                        json_data = json.loads(response)
                        album.wyy_count = json_data[self.wyy_api_sales]['data'][str(album.wyy_id)]
                        song_sales = json_data[self.wyy_api_song_sales]['data']
                        album.wyy_song_count = album.wyy_count * album.song_num
                        for song_sale in song_sales.values():
                            album.wyy_song_count += song_sale
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
                        count=count_today, money=money_today)

        artist_list = Artist.objects.annotate(album_sum=Sum('album__money'))
        for artist in artist_list:
            if artist.album_sum:
                artist.money = artist.album_sum
                artist.save()
