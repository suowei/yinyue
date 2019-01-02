from django.contrib import admin

from .models import Artist
from .models import Album

admin.site.register(Artist)
admin.site.register(Album)
