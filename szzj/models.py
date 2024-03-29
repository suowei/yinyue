from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)
    release_date = models.DateField()
    is_album = models.BooleanField(default=True)
    is_free = models.BooleanField(default=False)
    frequency = models.IntegerField(default=48)
    song_num = models.SmallIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    album_only = models.BooleanField(default=True)
    song_price = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    qq_id = models.IntegerField(null=True, blank=True)
    kugou_id = models.IntegerField(null=True, blank=True)
    kugou_album_id = models.IntegerField(null=True, blank=True)
    kuwo_id = models.CharField(max_length=20, null=True, blank=True)
    wyy_id = models.IntegerField(null=True, blank=True)
    wyy_params = models.TextField(null=True, blank=True)
    wyy_encSecKey = models.TextField(null=True, blank=True)
    migu_id = models.BigIntegerField(null=True, blank=True)
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
    migu_count = models.IntegerField(default=0)
    migu_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    count = models.IntegerField(default=0, db_index=True)
    money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00, db_index=True)

    def __str__(self):
        return self.title


class AlbumData(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    time = models.DateTimeField()
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
    migu_count = models.IntegerField(default=0)
    migu_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    count = models.IntegerField(default=0)
    money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)


class AlbumDataDaily(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    date = models.DateField()
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
    migu_count = models.IntegerField(default=0)
    migu_money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    count = models.IntegerField(default=0)
    money = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)


class AlbumInfo(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    sale_time = models.DateTimeField()
    info = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Tour(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.artist.name + self.title


class City(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Site(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    seats = models.IntegerField(default=0)

    def __str__(self):
        return self.city.name + self.name


class Concert(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    date = models.DateTimeField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def __str__(self):
        return self.tour.__str__() + self.date.__str__() + self.site.__str__()
