from django.db import models


class City(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Theatre(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.city.name + self.name


class Stage(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    seats = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.theatre.name + self.name


class Produce(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Musical(models.Model):
    produce = models.ForeignKey(Produce, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=50, unique=True)
    is_original = models.BooleanField(default=True)
    is_zhongwen = models.BooleanField(default=True)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    musical = models.ForeignKey(Musical, on_delete=models.CASCADE)
    seq = models.PositiveSmallIntegerField(default=0)
    job = models.CharField(max_length=50)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


class Role(models.Model):
    musical = models.ForeignKey(Musical, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    seq = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.musical.name + self.seq + self.name


class Tour(models.Model):
    musical = models.ForeignKey(Musical, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    cast = models.ManyToManyField(Artist, through='Tourcast')

    def __str__(self):
        return self.musical.name + self.name


class Schedule(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    no = models.PositiveSmallIntegerField(default=1)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    begin_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    theatre = models.ForeignKey(Theatre, on_delete=models.SET_NULL, blank=True, null=True)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, blank=True, null=True)


class Sale(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    info = models.TextField()  # 开票或优惠信息


class Tourcast(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


class Show(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    time = models.DateTimeField()
    cast = models.ManyToManyField(Artist, through='Showcast')


class Showcast(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
