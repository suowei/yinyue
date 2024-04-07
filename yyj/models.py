from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=20, unique=True)
    seq = models.PositiveSmallIntegerField(default=999)

    def get_absolute_url(self):
        return "/yyj/city/%i/" % self.id

    def __str__(self):
        return self.name


class Theatre(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def get_absolute_url(self):
        return "/yyj/theatre/%i/" % self.id

    def __str__(self):
        return self.name


class Stage(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    seats = models.PositiveSmallIntegerField(default=0)

    def get_absolute_url(self):
        return "/yyj/stage/%i/" % self.id

    def __str__(self):
        if self.name:
            return self.theatre.__str__() + self.name
        else:
            return self.theatre.__str__()


class Produce(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return "/yyj/produce/%i/" % self.id

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=50)
    note = models.CharField(max_length=50, blank=True, null=True)

    def get_absolute_url(self):
        return "/yyj/artist/%i/" % self.id

    def __str__(self):
        if self.note:
            return self.name + self.note
        else:
            return self.name


class Musical(models.Model):
    produces = models.ManyToManyField(Produce, through='MusicalProduces')
    name = models.CharField(max_length=50, unique=True)
    is_original = models.BooleanField(default=True)
    SETUP = 'ZZ'
    PROMOTE = 'DD'
    PRESENT = 'SS'
    PROGRESS_CHOICES = [
        (SETUP, '制作'),
        (PROMOTE, '定档'),
        (PRESENT, '上演'),
    ]
    progress = models.CharField(
        max_length=2,
        choices=PROGRESS_CHOICES,
        default=SETUP,
    )
    premiere_date = models.DateField()
    premiere_date_text = models.CharField(max_length=20, blank=True, null=True)
    info = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        return "/yyj/musical/%i/" % self.id

    def __str__(self):
        return self.name


class MusicalProduces(models.Model):
    musical = models.ForeignKey(Musical, on_delete=models.CASCADE)
    seq = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=20, default="出品制作")
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)


class MusicalStaff(models.Model):
    musical = models.ForeignKey(Musical, on_delete=models.CASCADE)
    seq = models.PositiveSmallIntegerField(default=1)
    job = models.CharField(max_length=50)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    def __str__(self):
        return self.musical.name + self.job + self.artist.name


class Role(models.Model):
    musical = models.ForeignKey(Musical, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    seq = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.seq.__str__() + ' ' + self.name


class MusicalCast(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    seq = models.PositiveSmallIntegerField(default=1)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'artist')

    def __str__(self):
        return self.role.seq.__str__() + ' ' + self.role.name + ' ' + self.seq.__str__() + ' ' + self.artist.name


class Tour(models.Model):
    musical = models.ForeignKey(Musical, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    is_long_term = models.BooleanField(default=False)
    begin_date = models.DateField()
    end_date = models.DateField()

    def get_absolute_url(self):
        return "/yyj/tour/%i/" % self.id

    def __str__(self):
        if self.name:
            return self.musical.name + self.name
        else:
            return self.musical.name


class Schedule(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    is_long_term = models.BooleanField(default=False)
    begin_date = models.DateField()
    end_date = models.DateField()
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return "/yyj/schedule/%i/" % self.id

    def __str__(self):
        return self.tour.__str__() + ' ' + self.begin_date.__str__() \
               + ' ' + self.end_date.__str__() + ' ' + self.stage.__str__()


class Show(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    time = models.DateTimeField()
    cast = models.ManyToManyField(MusicalCast, blank=True)

    def __str__(self):
        return self.schedule.__str__() + ' ' + self.time.__str__()


class Conflict(models.Model):
    time = models.DateTimeField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    def __str__(self):
        return self.time.__str__() + ' ' + self.artist.__str__()


class Chupiao(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    par_value = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seat = models.CharField(max_length=100)
    xianyu = models.TextField()
    note = models.CharField(max_length=100, null=True, blank=True)

    def get_absolute_url(self):
        return "/yyj/chupiao/%i/" % self.id

    def __str__(self):
        return self.user.__str__() + ' ' + self.show.__str__()
