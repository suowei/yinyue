from django.db import models
from urllib import request, parse
import json
from decimal import Decimal


class Album(models.Model):
    title = models.CharField(max_length=200)
    singer = models.CharField(max_length=200)
    release_date = models.DateField()
    song_num = models.SmallIntegerField()
    price = models.DecimalField(max_digits=4, decimal_places=2)
    album_only = models.BooleanField(default=True)
    song_price = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    qq_id = models.IntegerField(null=True, blank=True)
    kugou_id = models.IntegerField(null=True, blank=True)
    kugou_hashs = models.TextField(null=True, blank=True)
    kuwo_id = models.CharField(max_length=20, null=True, blank=True)
    wyy_id = models.IntegerField(null=True, blank=True)
    wyy_params = models.TextField(null=True, blank=True)
    wyy_encSecKey = models.TextField(null=True, blank=True)
    xiami_id = models.IntegerField(null=True, blank=True)
    migu_id = models.CharField(max_length=20, null=True, blank=True)
    qq_count = models.IntegerField(default=0)
    qq_song_count = models.IntegerField(default=0)
    qq_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    kugou_count = models.IntegerField(default=0)
    kugou_song_count = models.IntegerField(default=0)
    kugou_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    kuwo_count = models.IntegerField(default=0)
    kuwo_song_count = models.IntegerField(default=0)
    kuwo_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    wyy_count = models.IntegerField(default=0)
    wyy_song_count = models.IntegerField(default=0)
    wyy_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    xiami_count = models.IntegerField(default=0)
    xiami_song_count = models.IntegerField(default=0)
    xiami_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    migu_count = models.IntegerField(default=0)
    migu_song_count = models.IntegerField(default=0)
    migu_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00, db_index=True)

    def get_sale_info(self):
        self.get_qq_sale_info()
        self.get_kugou_sale_info()
        self.get_kuwo_sale_info()
        self.get_wyy_sale_info()
        self.get_xiami_sale_info()
        self.get_migu_sale_info()
        self.money = self.qq_money + self.kugou_money + self.kuwo_money + self.wyy_money + self.xiami_money + self.migu_money

    def get_qq_sale_info(self):
        if self.qq_id is None:
            return
        url = 'https://c.y.qq.com/v8/fcg-bin/musicmall.fcg?cmd=get_album_buy_page&albumid=' + self.qq_id.__str__()
        with request.urlopen(url) as f:
            data = f.read().decode('gbk')
            json_data = json.loads(data[18:-1])
            info = json_data['data']['sale_info']
            self.qq_count = info['album_count']
            self.qq_song_count = info['total_song_count']
            self.qq_money = Decimal(info['sale_money'])

    def get_kugou_sale_info(self):
        if self.kugou_id is None:
            return
        url = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getBuyNum?topic_id=' + self.kugou_id.__str__()
        with request.urlopen(url) as f:
            data = f.read().decode('utf-8')
            json_data = json.loads(data)
            self.kugou_count = json_data['buy_num']
            if self.album_only:
                self.kugou_money = self.price * self.kugou_count
            else:
                url2 = 'https://zhuanjidata.kugou.com/v3/Commoncharge/getSongsInfo?topic_id=' + self.kugou_id + '&hashs=' + self.kugou_hashs
                with request.urlopen(url2) as f2:
                    data2 = f2.read().decode('utf-8')
                    json_data2 = json.loads(data2)
                    song_sales = json_data2['data']
                    self.kugou_song_count = 0
                    for song_sale in song_sales:
                        self.kugou_song_count += song_sale['buy_count']
                    self.kugou_money = self.price * self.kugou_count + (self.kugou_song_count - self.kugou_count * self.song_num) * self.song_price

    def get_kuwo_sale_info(self):
        if self.kuwo_id is None:
            return
        data = {'key': self.kuwo_id, 'op': 'gfc'}
        req = request.Request('http://vip1.kuwo.cn/fans/admin/sysInfo', data=parse.urlencode(data).encode('utf-8'))
        with request.urlopen(req) as f:
            response = f.read().decode('utf-8')
            json_data = json.loads(response)
            docs = json_data['fans']['docs']
            self.kuwo_count = int(docs['total_cnt'])
            self.kuwo_song_count = int(docs['song_total_cnt'])
        data2 = {'type': self.kuwo_id}
        req2 = request.Request('http://vip1.kuwo.cn/fans/promotion/gettotalcnt', data=parse.urlencode(data2).encode('utf-8'))
        with request.urlopen(req2) as f:
            response2 = f.read().decode('utf-8')
            json_data2 = json.loads(response2)
            self.kuwo_money = Decimal(json_data2['data']['totalMoney'])

    def get_wyy_sale_info(self):
        if self.wyy_id is None:
            return
        data = {'params': self.wyy_params, 'encSecKey': self.wyy_encSecKey}
        req = request.Request('https://music.163.com/weapi/vipmall/albumproduct/detail', data=parse.urlencode(data).encode('utf-8'))
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.116')
        req.add_header('Cookie', '_iuqxldmzr_=32; _ntes_nnid=6f5d1bca43ec729e8282602fb832fda6,1544339887101; _ntes_nuid=6f5d1bca43ec729e8282602fb832fda6; __utmz=94650624.1544339888.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); WM_TID=fOqk5KJk8dRAQBFBEBd8b9dXsnCTxHUE; JSESSIONID-WYYY=f1bPtYWmY56lpA4QwvyQSe%2FjiCQkvM0Betc%2FHOkxZzfiDnlKjeKglOXmvTXQ7AbBV9PzSsbm%2BziUVlJhjeP7xKR0wmt5Po9rqsS5Ed8di0c2TWpPgwxRwfxpO2Vn%2F3qi9738C1GxtNZgZSCsuFdSu9bzr4sMhwJ3Y3aM6%5CX7725iF7YN%3A1544530566006; __utma=94650624.1924053452.1544339888.1544439650.1544528767.3; __utmc=94650624; WM_NI=hHAptLBX1Prj7Rff4OKPwlgZplx0SmlkRc9%2F5TtejVhC3BqECF%2Bj%2Fam6UdijxEdcvjgEdntU15w2VB%2FmFG73jEElfaqsAmlaUh3pe%2BxjFhg31D3dfP8BD90AvHKkiZ6cRmY%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8ff25289abb9d3bc4b92ef8ba7c55b828b8f84f36af794b7b7e939a1b9acb7f82af0fea7c3b92aac988f91f7488288ffb1f162f58eaa87b7458990b98de652b4b4b8d1d267b0b59e84bc25f78cbc86e95eac9dfda3f44f819ae58bae6bafea9b85ec62bc9bac84f562a59bac8ff75ff3ebb9d3d54aedb38aa8b639aa9b8b8de56bb3ad8f8eef6b97b8fd91e821bcb68a89e639f39cfd85e55cfc9e8cdab34bb698858cec52f6bd9e8edc37e2a3; __utmb=94650624.4.10.1544528767')
        with request.urlopen(req) as f:
            response = f.read().decode('utf-8')
            json_data = json.loads(response)
            info = json_data['product']
            self.wyy_count = info['saleNum']
            self.wyy_song_count = info['songSales']
            self.wyy_money = self.price * self.wyy_count
            if not self.album_only:
                self.wyy_money += (self.wyy_song_count - self.wyy_count * self.song_num) * self.song_price

    def get_xiami_sale_info(self):
        return

    def get_migu_sale_info(self):
        if self.migu_id is None or self.migu_id != '24388243':
            return
        url = 'https://app.act.nf.migu.cn/MAC/activity3/ninepercent/getAlbumInfo?activityId=NINEPERCENT'
        req = request.Request(url)
        req.add_header('channel', '014000D')
        req.add_header('ua', 'Android_migu')
        req.add_header('uid', '1ae26295-9758-49bc-9c27-c6db2f76cb48')
        req.add_header('version', '6.4.1')
        with request.urlopen(req) as f:
            data = f.read().decode('utf-8')
            json_data = json.loads(data)
            self.migu_count = json_data['data']['albumSoldNum']
            self.migu_money = self.price * self.migu_count
