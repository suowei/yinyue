from django.contrib import admin

from .models import Artist
from .models import Album
from .models import AlbumData
from .models import AlbumDataDaily
from .models import AlbumInfo
from .models import Tour
from .models import City
from .models import Site
from .models import Concert


class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['name']


class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields = ['artist']


class AlbumInfoAdmin(admin.ModelAdmin):
    autocomplete_fields = ['artist']


class AlbumDataAdmin(admin.ModelAdmin):
    autocomplete_fields = ['album']


class TourAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields = ['artist']


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']


class SiteAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['city']


class ConcertAdmin(admin.ModelAdmin):
    autocomplete_fields = ['tour', 'site']


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumData, AlbumDataAdmin)
admin.site.register(AlbumDataDaily)
admin.site.register(AlbumInfo, AlbumInfoAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Concert, ConcertAdmin)
