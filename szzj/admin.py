from django.contrib import admin

from .models import Singer
from .models import Album

admin.site.register(Singer)
admin.site.register(Album)
