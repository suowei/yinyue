from django.contrib import admin

from .models import Artist
from .models import Album
from .models import AlbumInfo
from .models import Tour
from .models import City
from .models import Site
from .models import Concert

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(AlbumInfo)
admin.site.register(Tour)
admin.site.register(City)
admin.site.register(Site)
admin.site.register(Concert)
