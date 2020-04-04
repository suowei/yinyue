from django.core.management.base import BaseCommand
from Crypto.Cipher import AES
import base64
import codecs
from szzj.models import Album


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
    help = 'Get wyy params.'

    wyy_g = '0CoJUm6Qyw8W8jud'
    wyy_b = "010001"
    wyy_c = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    wyy_i = '0123456789abcdef'
    wyy_iv = "0102030405060708"

    def handle(self, *args, **options):
        album_list = Album.objects.all()
        for album in album_list:
            if album.wyy_params:
                wyy_enc_text = str({
                    '/api/vipmall/albumproduct/album/query/sales': '{albumIds:' + str(album.wyy_id) + '}',
                    '/api/vipmall/albumproduct/album/query/song/sales': '{albumId:' + str(album.wyy_id) + '}'
                })
                album.wyy_params = aes_encrypt(aes_encrypt(wyy_enc_text, self.wyy_g, self.wyy_iv), self.wyy_i, self.wyy_iv)
                album.wyy_encSecKey = rsa_encrypt(self.wyy_i, self.wyy_b, self.wyy_c)
                album.save()
